# ns-client-disabled-check
Script to find devices with inactive Netskope Clients

## Summary of the Request
Customer wants the ability to find which devices/endpoints are actually disabled/offline, so they can locate the devices and get them back online.

## Usage

```
USAGE: python3 ns_client_disabled_check.py <tenant> <token_v1> <event_timeperiod> <device_limit>
    tenant: example.goskope.com
    token_v1: Netskope APIv1 token
    event_timeperiod: How far back (in seconds) to look for correlating events. Recommend starting with 86400 (1 day).
    device_limit: Number of devices to fetch that are marked as "disabled" by Netskope. Recommend starting with 100. Maximum is 5000.
```

## Example Run with CSV Output
```
$ python ns_client_disabled_check.py example.goskope.com ffffffffffffffffffffffffffffffff 86400 100

Getting list of devices with Netskope Client marked as "disabled"...
Searching for events within the last 86400 seconds that correlate with each device...

"device_hostname","event_hostname","event_device","event_domain","event_timestamp","result"
"C02F83XXXXXX","unknown","github.com","1639497291","OKAY: Events found during set timeperiod"
"tabernarious","unknown","","","TROUBLESHOOT: No events found during set timeperiod"
"DESKTOP-XXXXXX1","unknown","","","TROUBLESHOOT: No events found during set timeperiod"
```