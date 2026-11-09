# Upstreaming idea (RFC, not a patch)

Current upstream behaviour: `quirk_apple_poweroff_thunderbolt()` (Lukas Wunner, Cactus Ridge 4C, suspend-late only).

What would be needed for the runtime case on Falcon Ridge 2C Macs:
1. Match `8086:156b` (and the other Apple-shipped Thunderbolt generations) on Apple hardware (`x86_apple_machine`).
2. Resolve `NHI0.SXFP`/`TRPE` (this firmware) in addition to `SXIO/SXFP/SXLV`.
3. A policy for "no device connected": runtime power-off via the ACPI methods when the Thunderbolt controller has
   no PCIe tunnel and the root port can enter D3, plus a hotplug path (the Apple firmware wakes the chip on
   cable insertion through GPE, which needs checking).
4. Keep link-disable on the root port, otherwise the link retrains (observed here).

None of this is implemented or tested as a kernel change; the userspace scripts prove the hardware path works.
Before sending anything to linux-pci, test on more models and ask on the list whether runtime power-off belongs in
quirks.c, in `drivers/thunderbolt`, or in ACPI power-resource handling.
