import json

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Status
from .mqtt.mqtt_manager import MQTTManager

mqtt_manager = MQTTManager()

connected_clients = []



def receive_status(request):
    response = HttpResponse(content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    response.write('retry: 10000\n\n')

    connected_clients.append(response)

    return response


@csrf_exempt
def control_device(request):
    if request.method == 'POST':
        try:
            data = request.body.decode('utf-8')
            data = json.loads(data)
            lock = data.get("lock")

            status = Status.objects.latest('update_at')
            status_data = {
                'lock': status.lock,
                'door': status.door
            }
            if lock != status_data.get('lock'):
                if lock == 1 and status_data.get("door") == 1:
                    raise ValueError('door must be close before lock')
            mqtt_manager.send_control_to_esp8266(lock, int(status_data["door"]))

            after_status = Status.objects.latest('update_at')

            return JsonResponse({'message': 'Control command sent to ESP8266', **after_status}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
