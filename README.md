# ns-client-disabled-check
Script to find devices with inactive Netskope Clients

## Summary of the Request
Customer wants the ability to find which devices/endpoints are actually disabled/offline, so they can locate the devices and get them back online.

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
