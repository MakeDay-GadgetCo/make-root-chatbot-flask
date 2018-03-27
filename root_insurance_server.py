import re
import json
import requests
from flask import request
from flask import Flask


ROOT_API_ENDPOINT = 'https://sandbox.root.co.za/v1/insurance'
API_KEY = 'api key here'
GET_MODELS_ROUTE = '/modules/root_gadgets/models'

app = Flask(__name__)

@app.route('/get-device-quote', methods=['GET', 'POST'])
def get_device_quote():
    request_body = json.loads(request.data)
    requested_device = request_body['result']['parameters']['device']
    response = get_available_devices()
    if response.status_code == 200:
        devices_dict = json.loads(response.text)

    filtered_devices = filter_matching_devices(requested_device, devices_dict)
    if len(filtered_devices) > 0:
        response_message = "Comprehensive insurance for {} is {}".format(requested_device, float(filtered_devices[0]['value'] / 100))
        return json.dumps({"messages":[{"speech": response_message, "type": 0}]})
    else:
        generic_devices = generic_filter_devices(requested_device, devices_dict)
        if len(generic_devices) > 0:
            suggestions = build_suggestions(generic_devices, requested_device)
        return json.dumps({"messages": suggestions})


def get_available_devices():
    return requests.get(ROOT_API_ENDPOINT + GET_MODELS_ROUTE, auth=(API_KEY, ''))


def filter_matching_devices(req_device, found_devices):
    # Match requested devices against found devices using regex
    return [device for device in found_devices if re.search(req_device, device['name']) is not None]


def generic_filter_devices(req_device, found_devices):
    # Check is requested device is a substring of any of the found devices (lower cased & spaces removed)
    # Eg. iphone6 is a substring iphone612gblte
    formatted_req_device = req_device.replace(" ", "").lower()
    return [device for device in found_devices if formatted_req_device in device['name'].replace(" ", "").lower()]


def build_suggestions(devices, req_device):
    response_message = "Sorry found no quotes for {}.".format(req_device)
    response_message += "\n I found other devices using {}".format(req_device)
    suggestions = [{"speech": response_message, "type": 0}]

    # If there are more than five suggestions, just take the first five.
    suggestion_limit = 5 if len(devices) > 5 else len(devices)

    for i in xrange(suggestion_limit):
        device_premium = "{} - R{}".format(devices[i]['name'], float(devices[i]['value'] / 100))
        suggestions.append({"speech": device_premium, "type": 0})
    return suggestions
