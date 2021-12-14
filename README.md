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
$ python ns_client_disabled_check.py dtavernier.goskope.com ffffffffffffffffffffffffffffffff 86400 100

Getting list of devices with Netskope Client marked as "disabled"...
Searching for events within the last 86400 seconds that correlate with each device...

"device_hostname","event_hostname","event_device","event_domain","event_timestamp","result"
"C02F83XXXXXX","unknown","github.com","1639497291","OKAY: Events found during set timeperiod"
"tabernarious","unknown","","","TROUBLESHOOT: No events found during set timeperiod"
"DESKTOP-XXXXXX1","unknown","","","TROUBLESHOOT: No events found during set timeperiod"
```

## Proposed Method
(since the Devices page is not very accurate)

Build a script that…
* Pulls a list of devices marked “disabled”
* Then for each “disabled” device, look for recent activity (in Skope IT)
* Print out a status for each device, something like:
  * "Device","OS","User","Last Seen Page Event"
  * "C02F83DQMD6T","Mac","jesse@mycorp.net","none"
  * "WSAMZN-2FT878E3","Windows Server","mel@mycorp.net","2021-12-11 09:25:08 CST"
  * "DESKTOP-VDGSDDU","Windows","pat@mycorp.net","2021-12-11 16:54:33 CST"

Notes:
* I could make the output “prettier” for the CLI, but CSV seems more useful depending on the number. If it’s easy I could print it to the screen in a pretty fashion and optionally dump a CSV as a local file.