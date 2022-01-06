##################################################
## Summary:     Script to find devices with inactive Netskope Clients
## Author:      Daniel Tavernier and Jorge Garza, Netskope SEs
## Last Update: 2022-01-06
## Version:     0.2
##################################################

import json
import socket
import sys
import urllib.request, urllib.parse
import argparse
from getpass import getpass

# Argument Usage, Defaults, and Parsing
parser = argparse.ArgumentParser(description='Find devices with inactive Netskope Clients.')
parser.add_argument('--tenant', type=str, required=True, help='Name of Netksope Tenant: example.goskope.com')
parser.add_argument('--token_v1', type=str, required=False, help='Netskope APIv1 token. Leave blank to be prompted for token.')
parser.add_argument('--timeperiod', type=int, required=False, help='How far back (in seconds) to look for correlating events. Default is 86400 (1 day).')
parser.add_argument('--devicelimit', type=int, required=False, help='Number of devices to fetch that are marked as "disabled" by Netskope. Default is 100. Maximum is 5000.')
args = parser.parse_args()

tenant = args.tenant

if args.token_v1:
    token_v1 = args.token_v1
else:
    token_v1 = getpass(prompt='Enter Netskope Tenant APIv1 Token: ')

if args.timeperiod:
    event_timeperiod = args.timeperiod
else:
    event_timeperiod = 86400

if args.devicelimit:
    device_limit = args.devicelimit
else:
    device_limit = 100

print()
print('Tenant Name:  ', args.tenant)
print('Time Period:  ', event_timeperiod)
print('Device Limit: ', device_limit)


# Set socket timeout. Default is indefinite, so without API calls will hang the script. 
socket_timeout = 10 # seconds
socket.setdefaulttimeout(socket_timeout)


def get_devices(tenant, token, device_query, limit=5000):
    # Define path for this API endpoint
    api_path = "/api/v1/clients"

    # URL encode query string (e.g. turn spaces into "%20")
    device_query_encoded = urllib.parse.quote(device_query)
 
    # Build full query string to send to the API endpoint
    query_string = f"token={token}&limit={limit}&query={device_query_encoded}"

    # Build full request URL
    url = f"https://{tenant}{api_path}?{query_string}"

    # Send request to API and save response
    response = urllib.request.urlopen(url)

    # Decode response for JSON parsing
    response_json = json.loads(response.read().decode("utf-8"))

    # Extract list of device hostnames
    disabled_devices = [devices['attributes']['host_info']['hostname'] for devices in response_json['data']]

    return disabled_devices


def get_events(tenant, token, event_query, event_type="page", timeperiod="86400", limit="1"):
    # Define path for this API endpoint
    api_path = "/api/v1/events"

    # URL encode query string (e.g. turn spaces into "%20")
    event_query_encoded = urllib.parse.quote(event_query)

    # Build full query string to send to the API endpoint
    query_string = f"token={token}&type={event_type}&timeperiod={timeperiod}&limit={limit}&query={event_query_encoded}"

    # Build full request URL
    url = f"https://{tenant}{api_path}?{query_string}"

    try:
        # Send request to API and save response
        response = urllib.request.urlopen(url)

        # Decode response for JSON parsing
        response_json = json.loads(response.read().decode("utf-8"))

        # Extract event data
        event_data = response_json['data'][0]
        event_response_status = 0 # API responded with data
    except socket.timeout:
        #print("ERROR: API timeout for " + api_path)
        event_data = ""
        event_response_status = 2 # API timed out
    except:
        #print("ERROR: No data)
        event_data = ""
        event_response_status = 1 # Could not parse data (likely no data returned)

    return event_response_status, event_data


def find_devices_with_disabled_clients(tenant, token, timeperiod="86400", device_limit="100"):
    print()
    print('Getting list of devices with Netskope Client marked as "disabled"...')
    device_query = "last_event.status eq 0"
    disabled_devices = get_devices(tenant, token, device_query, device_limit)

    print(f"Searching for events within the last {timeperiod} seconds that correlate with each device...")

    # Print csv headers
    print()
    print('"device_hostname","event_domain","event_timestamp","result"')

    for device_hostname in disabled_devices:
        device_type = "unknown"
        event_query = "hostname eq " + device_hostname
        event_domain = ""
        event_timestamp = ""
        result = ""

        # Get thet last event for this device within the specified timeperiod
        event_response_status, event_data = get_events(tenant, token, event_query, "page", timeperiod, "1")
        if event_response_status == 0:
            event_domain = event_data["domain"]
            event_timestamp = event_data["timestamp"]
            result = "OKAY: Events found during set timeperiod"
        elif event_response_status == 1:
            result = "TROUBLESHOOT: No events found during set timeperiod"
        elif event_response_status == 2:
            result = "ERROR: API timed out; try again and or extend the timeout"
        else:
            result = "ERROR: Unknown response from event API"

        print(f'"{device_hostname}","{event_domain}","{event_timestamp}","{result}"')


devices_to_troubleshoot = find_devices_with_disabled_clients(tenant, token_v1, event_timeperiod, device_limit)
