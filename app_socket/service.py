import json


def convert_status_to_json(data):
    # Replace single quotes with double quotes
    data = data.replace("'", '"')
    # Add double quotes to keys
    data = data.replace('door', '"door"').replace('lock', '"lock"')
    # Convert to valid JSON
    json_data = json.loads(data)

    return json_data
