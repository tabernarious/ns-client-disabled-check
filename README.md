# ns-client-disabled-check
Script to find devices with inactive Netskope Clients

## Summary of the Request
Customer wants the ability to find which devices/endpoints are actually disabled/offline, so they can locate the devices and get them back online.

## Usage

```
usage: ns_client_disabled_check.py [-h] --tenant TENANT [--token_v1 TOKEN_V1] [--timeperiod TIMEPERIOD] [--devicelimit DEVICELIMIT]

Find devices with inactive Netskope Clients.

optional arguments:
  -h, --help            show this help message and exit
  --tenant TENANT       Name of Netksope Tenant: example.goskope.com
  --token_v1 TOKEN_V1   Netskope APIv1 token. Leave blank to be prompted for token.
  --timeperiod TIMEPERIOD
                        How far back (in seconds) to look for correlating events. Default is 86400 (1 day).
  --devicelimit DEVICELIMIT
                        Number of devices to fetch that are marked as "Disabled" by Netskope. Default is 100. Maximum is 5000.
  --showallusers        Lists all users configured for each device. This will also list devices with *any* user marked "Disabled".
```

## Example Run with CSV Output
```
$ python ns_client_disabled_check.py --tenant example.goskope.com
Enter Netskope Tenant APIv1 Token: ********

Tenant Name:   example.goskope.com
Time Period:   86400
Device Limit:  100
ShowAllUsers:  False

Getting list of devices with Netskope Client marked as "disabled"...
Searching for events within the last 86400 seconds that correlate with each device...

"device_hostname","device_username","device_os","device_os_version","device_client_version","device_user_client_status","device_user_client_actor","device_user_client_event","device_user_timestamp","event_domain","event_timestamp","result"
"C02F83XXXXXX","james@example.net","Mac","12.2.0","91.0.6.812","Enabled","System","Tunnel Up","2022-01-28 16:55:30","www.example.net","2022-01-28 21:32:15","OKAY: Enabled and events found during set timeperiod"
"tabern123","daniel@example.net","iOS","14.7.1","89.0.0.853","Disabled","System","Tunnel Down","2021-10-19 17:08:54","","","TROUBLESHOOT: Disabled and no events found during set timeperiod"
"DESKTOP-KZXXXXX","jesse@example.net","Windows","10.0 (2009)","87.0.0.704","Disabled","System","Tunnel Down","2021-08-24 15:42:17","","","TROUBLESHOOT: Disabled and no events found during set timeperiod"
"DESKTOP-KPXXXXX","(no user)","Windows","10.0 (2009)","87.0.0.704","Enabled","System","Tunnel Up","2021-05-07 11:53:47","","","TROUBLESHOOT: Enabled but no events found during set timeperiod"
```