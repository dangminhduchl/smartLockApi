import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from smartLock.utils import RedisSingleton
from .models import Status, Request

connected_clients = []


def receive_status(request):
    response = HttpResponse(content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    response.write('retry: 10000\n\n')

    connected_clients.append(response)

    return response



class ControlDevice(APIView):
    permission_classes = (IsAuthenticated,)

    @csrf_exempt
    def post(self, request):
        data = request.body.decode('utf-8')
        data = json.loads(data)
        lock = data.get("lock")

        status = Status.objects.latest('update_at')
        status_data = {
            'lock': status.lock,
            'door': status.door
        }
        if lock != status_data.get('lock'):
            request_status = Status.objects.create(lock=lock, door=int(status_data["door"]))
            if lock == 1 and status_data.get("door") == 0:
                raise ValueError('door must be close before lock')
            redis = RedisSingleton().get_non_async_instance()
            redis.publish("control", lock)

            after_status = Status.objects.latest('update_at')
            after_status_data = {
                'lock': int(after_status.lock),
                'door': int(after_status.door)
            }
            after_status = Status.objects.create(lock=lock, door=int(status_data["door"]))
            Request.objects.create(action_id=after_status.id, request_id=request_status.id, user=request.user)
            return JsonResponse({'message': 'Control command sent to ESP8266', **after_status_data}, status=200)

        return JsonResponse({'error': 'Invalid request method'}, status=405)
