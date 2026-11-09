Title: Idle power: CPU package never reaches pc6 on MacBookAir7,2 - cause and fix

Package C-states stop at pc3 because the Thunderbolt controller (DSL5320) is always powered with ASPM disabled and the
FaceTime camera has ASPM off. Cutting Thunderbolt power via the SSDT method `SXFP` (GPIO47) and forcing L1 on the
camera brings pc6 to ~65% and idle power from ~9.0 W to ~6.2 W (total system, AC, SMC PSTR).
Scripts and notes: <REPO-URL>. Tested on Ubuntu 26.04.1 / kernel 7.0.0-43 only. Cost: Thunderbolt/Mini DisplayPort
port is off until `mac-tbpower on`.
