# macbookair72-linux-power

**Cut idle power by roughly 25-30% on a MacBook Air 2015-2017 (MacBookAir7,2) under Linux.**

On this model Linux never lets the CPU package reach deep sleep (`pc6` = 0%, stuck at `pc3`),
because two PCIe links never go idle: the always-powered **Thunderbolt 2 controller**
(Intel DSL5320 "Falcon Ridge 2C") and the **FaceTime HD camera** (BIOS leaves its ASPM off).
Cutting power to the Thunderbolt chip through the Apple ACPI method (`SXFP`) and enabling
ASPM L1 on the camera brings `pc6` to ~65% and the system draw down from ~9.0 W to ~6.2 W
at idle with the screen at full brightness.

> Status: **works on one machine** (MacBookAir7,2, Ubuntu 26.04.1, kernel 7.0.0-43, Broadwell
> i5-5350U). It talks to ACPI methods and PCH GPIO directly. Use at your own risk, and
> please report results from other machines (see "Reporting results").

## Results

Measured as total system power from the Apple SMC key `PSTR` (works on AC and battery, cross-checked
against `PDTR - PSTR` = battery charge current). Clean desktop after reboot, brightness 100%,
3 pairs of 30 s runs:

| Condition | Thunderbolt on | Thunderbolt off |
|---|---|---|
| Idle desktop | 8.83 / 9.01 / 9.18 W (avg 9.0) | 6.61 / 6.78 / 5.29 W (avg 6.2) |
| Screen off | 5.2-5.4 W | 3.0 W (-42%) |
| Chrome open (13% CPU) | 11.1 W | 9.1-9.6 W |
| CPU package (RAPL), idle | 2.5 W | 1.2 W |
| Package pc6 residency | 0% | ~65% |

Run-to-run spread within a series is 0.3-0.9 W, so the effect is well outside noise.
Video playback on battery (Chrome, RuTube H.264 with VAAPI, brightness 50%, discharging, interleaved A-B-A, 3 x 30 s each,
total system power from SMC `PSTR`, matches battery `current x voltage`):

| Run | Fix | Total power | Package pc6 |
|---|---|---|---|
| A1 | on  | 7.17 / 7.29 / 7.38 W (avg 7.28) | ~27% |
| B  | off (Thunderbolt powered) | 10.12 / 9.27 / 9.15 W (avg 9.51) | 0% |
| A2 | on  | 7.15 / 7.20 / 7.53 W (avg 7.29) | ~29% |

-2.2 W, about 23%. With a 53 Wh battery that is roughly 7.3 h instead of 5.6 h of video (calculated, not a full
discharge test). In run B only the Thunderbolt part is reverted; the camera ASPM change stays until reboot,
so the true "before" is slightly worse than B.

## Install

```
git clone <this repo> && cd macbookair72-linux-power
sudo ./install.sh        # installs acpi-call-dkms, scripts, systemd unit and a resume hook
sudo mac-tbpower status
```

Revert: `sudo ./uninstall.sh` (restores Thunderbolt power first).

**Cost:** the Thunderbolt / Mini DisplayPort port is unpowered. For an external display run
`sudo mac-tbpower on`, and `sudo mac-tbpower off` afterwards.

## How it works (short)

1. Thunderbolt power on these Macs is a PCH GPIO (**GPIO47**, pad register at I/O `0x978`),
   controlled from the firmware's SSDT **"PcieTbt"** (not the DSDT, which is why `strings DSDT`
   finds nothing). `\_SB.PCI0.RP05.UPSB.DSB0.NHI0.SXFP(0)` drives it low; `TRPE(1,ms)` releases
   it and trains the link.
2. The kernel has `quirk_apple_poweroff_thunderbolt()`, but it only covers Cactus Ridge 4C, only
   runs at suspend, and calls `SXIO/SXFP/SXLV` that this model does not have under those names.
3. Before cutting power we unload `thunderbolt`, remove the PCI device and set Link Disable on the
   root port `00:1c.4`, otherwise the link just retrains.
4. After every resume the root port comes back with the link enabled and `pc6` disappears again,
   so a sleep hook re-applies everything. **systemd 259 only runs hooks from
   `/usr/lib/systemd/system-sleep/`** (not `/etc/`).
5. The camera (`14e4:1570`, `02:00.0`) needs ASPM L1 forced on both ends.
   Both fixes are needed: either alone leaves `pc6` at 0%.

Details: [docs/ACPI.md](docs/ACPI.md), [docs/DIAGNOSE.md](docs/DIAGNOSE.md),
[docs/PORTING.md](docs/PORTING.md), [docs/MEASUREMENTS.md](docs/MEASUREMENTS.md),
[docs/KERNEL.md](docs/KERNEL.md).

## What did not help (so you don't repeat it)

- Runtime PM on xHCI/MEI/LPC/thermal/DMA + card-reader autosuspend: within noise.
- `pc7` stays at 0% under every condition tried (screen off, Wi-Fi/BT off, card reader and camera
  removed, keyboard disconnected). Package limit in MSR 0xE2 is unlimited. Open suspects: SSD LTR,
  xHCI with the internal keyboard, display engine without PSR (this panel has none).
- FBC is off because Mutter 50 prefers a 10-bit XR30 framebuffer that Broadwell FBC cannot compress.
- Brightness does matter: 100% ~9.4 W, 50% ~8.2 W, 10% ~7.2 W.
- Unloading `thunderbolt`, runtime-suspending it, or removing its PCI devices *without* cutting
  power gives only ~0.3 W.
- Dangerous on this SSD (Apple SM0128G, data loss reported): `pcie_aspm=powersupersave`,
  `acpi_osi=!Darwin`, `powertop --auto-tune`, TLP over power-profiles-daemon.

## Reporting results

Open an issue with: `cat /sys/class/dmi/id/product_name`, `uname -r`, `sudo turbostat --quiet
--show Pkg%pc2,Pkg%pc3,Pkg%pc6,Pkg%pc7,PkgWatt --interval 15 --num_iterations 1` before and after,
and wall power (or `tools/pmeas.py`). Other Thunderbolt-equipped Macs (MacBookAir6,x/7,x,
MacBookPro11,x/12,x, 2014-2017) probably have the same structure with different PCI/GPIO numbers;
see docs/PORTING.md.

## Related work

- [flo-at-work/thunderbolt-disable-mba2014](https://github.com/flo-at-work/thunderbolt-disable-mba2014):
  the same idea for MacBook Air 2014 (Thunderbolt power logic in SSDT, ~1 W idle).
- [mkottman/acpi_call](https://github.com/mkottman/acpi_call): the module used to call ACPI methods.
- Kernel: `drivers/pci/quirks.c`, `quirk_apple_poweroff_thunderbolt()`.

License: MIT. The ACPI excerpts in `docs/ACPI.md` are short quotations for interoperability;
full firmware tables are not included.

## Packaging

`packaging/macbookair72-power_0.1.0_all.deb` is built from `packaging/deb-root` (files in `/usr/sbin`, service in
`/lib/systemd/system`). It has **not** been installed from the .deb yet; only `dpkg-deb -c` content was checked.
The service is enabled only when `product_name` is `MacBookAir7,2`.
