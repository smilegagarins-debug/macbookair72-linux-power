Title: MacBook Air 2015-2017 (MacBookAir7,2) on Ubuntu 26.04: -2.5 W at idle by powering off Thunderbolt

Symptom: ~9 W idle, CPU package never deeper than pc3 (turbostat: pc6/pc7 = 0%).
Cause: always-powered Thunderbolt controller (Falcon Ridge 2C) and FaceTime camera with no ASPM.
Fix: ACPI SSDT method SXFP via acpi_call + L1 on the camera, re-applied after resume.
Result: ~6.2 W idle, pc6 ~65%; package power 2.5 -> 1.2 W. Cost: Thunderbolt port off.
Repo with scripts and the diagnosis recipe: https://github.com/smilegagarins-debug/macbookair72-linux-power. Install: `sudo ./install.sh` (also a .deb in the repo).
Tested on one machine only; feedback and data from other Air/Pro models welcome.
Warning: calling ACPI methods can hang the machine; this SSD (Apple SM0128G) has a history of data loss with
aggressive power settings, which this fix does not touch.
