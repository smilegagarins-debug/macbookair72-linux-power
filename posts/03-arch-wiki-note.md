### Idle power (MacBookAir7,2)

If `turbostat` shows `Pkg%pc6` at 0% on an idle desktop, the Thunderbolt controller and the FaceTime camera PCIe
links are the cause. See <REPO-URL> for a script that powers the Thunderbolt controller off through the Apple ACPI
method (`SXFP`, PCH GPIO47) and enables ASPM L1 on the camera. It disables the Thunderbolt/Mini DisplayPort port
until re-enabled. Tested on one machine; use `acpi_call` (`acpi_call-dkms` on Arch).
