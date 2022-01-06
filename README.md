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
                        Number of devices to fetch that are marked as "disabled" by Netskope. Default is 100. Maximum is 5000.
```

## Example Run with CSV Output
```
$ python ns_client_disabled_check.py --tenant example.goskope.com
Enter Netskope Tenant APIv1 Token: 

Tenant Name:   example.goskope.com
Time Period:   86400
Device Limit:  100

Getting list of devices with Netskope Client marked as "disabled"...
Searching for events within the last 86400 seconds that correlate with each device...

"device_hostname","event_domain","event_timestamp","result"
"C02F83XXXXXX","example.weebly.com","1641490000","OKAY: Events found during set timeperiod"
"tabern123","","","TROUBLESHOOT: No events found during set timeperiod"
"DESKTOP-KXXXXXX","","","TROUBLESHOOT: No events found during set timeperiod"
```