from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Status
from .mqtt.mqtt_manager import MQTTManager

mqtt_manager = MQTTManager()


def receive_status(request):
    try:
        status = Status.objects.latest('update_at')
        status_data = {
            'lock': status.lock,
            'door': status.door
        }
        return JsonResponse(status_data, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def control_device(request):
    if request.method == 'POST':
        try:
            data = request.POST
            lock = int(data.get('lock'))

            status = Status.objects.latest('update_at')
            status_data = {
                'lock': status.lock,
                'door': status.door
            }

            mqtt_manager.send_control_to_esp8266(lock,status_data["door"])

            return JsonResponse({'message': 'Control command sent to ESP8266', **status_data}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)