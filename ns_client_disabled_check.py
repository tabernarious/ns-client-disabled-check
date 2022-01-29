##################################################
## Summary:     Script to find devices with inactive Netskope Clients
## Author:      Daniel Tavernier and Jorge Garza, Netskope SEs
## Last Update: 2022-01-06
## Version:     0.3
##################################################

import datetime
import json
import socket
#import sys
import urllib.request, urllib.parse
import argparse
from getpass import getpass

# Argument Usage, Defaults, and Parsing
parser = argparse.ArgumentParser(description='Find devices with inactive Netskope Clients.')
parser.add_argument('--tenant', type=str, required=True, help='Name of Netksope Tenant: example.goskope.com')
parser.add_argument('--token_v1', type=str, required=False, help='Netskope APIv1 token. Leave blank to be prompted for token.')
parser.add_argument('--timeperiod', type=int, required=False, help='How far back (in seconds) to look for correlating events. Default is 86400 (1 day).')
parser.add_argument('--devicelimit', type=int, required=False, help='Number of devices to fetch that are marked as "Disabled" by Netskope. Default is 100. Maximum is 5000.')
parser.add_argument('--showallusers', action='store_true', help='Lists all users configured for each device. This will also list devices with *any* user marked "Disabled".')
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

show_all_users = args.showallusers

print()
print('Tenant Name:  ', tenant)
print('Time Period:  ', event_timeperiod)
print('Device Limit: ', device_limit)
print('ShowAllUsers: ', show_all_users)


# Set socket timeout. Default is indefinite, so without API calls will hang the script. 
socket_timeout = 10 # seconds
socket.setdefaulttimeout(socket_timeout)


def get_devices(tenant, token, device_query, limit=5000, show_all_users=False):
    # Define path for this API endpoint
    api_path = "/api/v1/clients"

    # URL encode query string (e.g. turn spaces into "%20")
    device_query_encoded = urllib.parse.quote(device_query)
 
    # Build full query string to send to the API endpoint
    query_string = f"token={token}&limit={limit}&query={device_query_encoded}"

    # Build full request URL
    url = f"https://{tenant}{api_path}?{query_string}"

    try:
        # Send request to API and save response
        response = urllib.request.urlopen(url)

        # Decode response for JSON parsing
        response_json = json.loads(response.read().decode("utf-8"))

        # Extract list of device hostnames
        #device_list = [devices['attributes']['host_info']['hostname'] for devices in response_json['data']]
        device_list = []

        # For each device loop through listed users and create duplicate duplicate device with relevant status
        #print(response_json['data'])
        for device_id in response_json['data']:
            attributes = device_id['attributes']

            for user in attributes['users']:
                dev_dict = {}
                dev_dict['device_hostname'] = attributes['host_info']['hostname']
                dev_dict['device_os'] = attributes['host_info']['os']
                dev_dict['device_os_version'] = attributes['host_info']['os_version']
                dev_dict['device_client_version'] = attributes['client_version']
                dev_dict['device_last_client_status'] = attributes['last_event']['status']
                dev_dict['device_last_client_event'] = attributes['last_event']['event']
                #dev_dict['device_client_install_time'] = attributes['client_install_time']
                try:
                    dev_dict['device_username'] = user['username']
                except:
                    dev_dict['device_username'] = "(no user)"
                dev_dict['device_user_client_actor'] = user['last_event']['actor']
                dev_dict['device_user_client_event'] = user['last_event']['event']
                dev_dict['device_user_client_status'] = user['last_event']['status']
                dev_dict['device_user_timestamp'] = datetime.datetime.fromtimestamp(user['last_event']['timestamp'])

                device_list.append(dev_dict)

                if show_all_users == False:
                    break

        device_list_response_status = 0 # API responded with data

    except socket.timeout:
        print("ERROR: API timeout for " + api_path)
        device_list = ""
        device_list_response_status = 2 # API timed out
        exit()
    except:
        print("ERROR: No data from " + api_path + " (confirm correct API token)")
        device_list = ""
        device_list_response_status = 1 # Could not parse data (likely no data returned or bad token)
        exit()

    return device_list_response_status, device_list


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
        #print("ERROR: No data from " + api_path)
        event_data = ""
        event_response_status = 1 # Could not parse data (likely no data returned)

    return event_response_status, event_data


def find_devices_with_disabled_clients(tenant, token, timeperiod="86400", device_limit="100", show_all_users=False):
    print()
    print('Getting list of devices with Netskope Client marked as "disabled"...')

    # The query for the clients API that will return "Disabled" devices. The query 'last_event.status eq 0' will return devices where any user's last event was "Disabled", even if the last overall event was "Enabled".
    device_query = "last_event.status eq 0"

    # Get a list of devices
    disabled_devices_response_status, disabled_devices = get_devices(tenant, token, device_query, device_limit, show_all_users)

    print(f"Searching for events within the last {timeperiod} seconds that correlate with each device...")

    # Print csv headers
    print()
    print('"device_hostname","device_username","device_os","device_os_version","device_client_version","device_user_client_status","device_user_client_actor","device_user_client_event","device_user_timestamp","event_domain","event_timestamp","result"')

    # Loop through devices returned from get_devices() function
    for device in disabled_devices:
        # Skip listing a device if the last status reported by any user was "Enabled". This is required because the query 'last_event.status eq 0' will return devices where any user's last event was "Disabled", even if the last overall event was "Enabled".
        if device['device_last_client_status'] == "Enabled" and show_all_users == False:
            continue

        device_hostname = device['device_hostname']
        device_username = device['device_username']
        device_os = device['device_os']
        device_os_version = device['device_os_version']
        device_client_version = device['device_client_version']
        device_user_client_actor = device['device_user_client_actor']
        device_user_client_event = device['device_user_client_event']
        device_user_client_status = device['device_user_client_status']
        device_user_timestamp = device['device_user_timestamp']
        #device_last_client_status = device['device_last_client_status']
        #device_last_client_event = device['device_last_client_event']

        if device_username == "(no user)":
            event_query = "hostname eq " + device_hostname
        else:
            event_query = "hostname eq " + device_hostname + " and user eq " + device_username
        event_domain = ""
        event_timestamp = ""
        result = ""

        # Get thet last event for this device within the specified timeperiod
        event_response_status, event_data = get_events(tenant, token, event_query, "page", timeperiod, "1")
        if event_response_status == 0:
            event_domain = event_data["domain"]
            event_timestamp = datetime.datetime.fromtimestamp(event_data["timestamp"])
            if device_user_client_status == "Disabled":
                result = "OKAY: Disabled but events found during set timeperiod"
            else:
                result = "OKAY: Enabled and events found during set timeperiod"
        elif event_response_status == 1:
            if device_user_client_status == "Disabled":
                result = "TROUBLESHOOT: Disabled and no events found during set timeperiod"
            else:
                result = "TROUBLESHOOT: Enabled but no events found during set timeperiod"
        elif event_response_status == 2:
            result = "ERROR: API timed out; try again and or extend the timeout"
        else:
            result = "ERROR: Unknown response from event API"

        print(f'"{device_hostname}","{device_username}","{device_os}","{device_os_version}","{device_client_version}","{device_user_client_status}","{device_user_client_actor}","{device_user_client_event}","{device_user_timestamp}","{event_domain}","{event_timestamp}","{result}"')


devices_to_troubleshoot = find_devices_with_disabled_clients(tenant, token_v1, event_timeperiod, device_limit, show_all_users)
