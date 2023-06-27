import ast
import json


def convert_status_to_json(data):
    # Replace single quotes with double quotes
    json_data = ast.literal_eval(data)

    return json_data
