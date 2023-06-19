def send_sse_event(event_data, connected_clients):
    for client in connected_clients:
        client.write('data: {}\n\n'.format(event_data))