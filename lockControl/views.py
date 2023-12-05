import json
import requests

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from smartLock.utils import RedisSingleton
from .models import Status, Request
from .serializer import RequestSerializer

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

        status = Status.objects.get(pk=2)
        status_data = {
            'lock': status.lock,
            'door': status.door
        }

        user = request.user
        response = requests.get(f"https://testnets-api.opensea.io/api/v2/chain/avalanche_fuji/account/{user.username}/nfts?collection=butterfly-791")
        data = response.json()
        nfts = data.get("nfts")
        is_access = False
        print(nfts)
        for nft in nfts:
            if nft.get("identifier") == "4":
                is_access = True
        if not is_access:
            return JsonResponse({'error': 'Invalid Key'}, status=403)

        if lock != status_data.get('lock'):
            request_status = Status.objects.create(lock=lock, door=int(status_data["door"]))
            if lock == 1 and status_data.get("door") == 0:
                raise ValueError('door must be close before lock')
            redis = RedisSingleton().get_non_async_instance()
            redis.publish("control", lock)

            after_status = Status.objects.get(pk=2)
            after_status_data = {
                'lock': int(after_status.lock),
                'door': int(after_status.door)
            }
            after_status = Status.objects.create(lock=lock, door=int(status_data["door"]))
            Request.objects.create(action_id=after_status.id, request_id=request_status.id, user=request.user)
            return JsonResponse({'message': 'Control command sent to ESP8266', **after_status_data}, status=200)

        return JsonResponse({'error': 'Invalid request method'}, status=405)


class HistoryDevice(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all requests
        all_requests = Request.objects.all()

        # Sort the requests based on query parameters (if provided)
        sort_by = request.GET.get('sort_by', 'created_at')
        order_by = request.GET.get('order_by', 'desc')  
        if sort_by:
            if order_by == 'desc':
                all_requests = all_requests.order_by(f'-{sort_by}')
            else:
                all_requests = all_requests.order_by(sort_by)

        # Initialize the paginator
        paginator = PageNumberPagination()
        # Define the number of requests per page (you can adjust this as needed)
        paginator.page_size = 10

        # Paginate the requests
        paginated_requests = paginator.paginate_queryset(all_requests, request)
        serializer = RequestSerializer(paginated_requests, many=True)

        return paginator.get_paginated_response(serializer.data)
