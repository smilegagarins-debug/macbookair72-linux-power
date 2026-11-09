Title: Same technique works on MacBookAir7,2 (Falcon Ridge 2C): data + scripts

Hi, thanks for this project. I followed the same idea on a MacBookAir7,2 (Air 2015-2017, i5-5350U,
Ubuntu 26.04.1, kernel 7.0.0-43) and it works there too, with different numbers:

- Power control lives in SSDT "PcieTbt": `\_SB.PCI0.RP05.UPSB.DSB0.NHI0.SXFP(0)` drives PCH GPIO47 low
  (pad register at I/O 0x978); `TRPE(1,ms)` powers it back and trains the link.
- Mainline `quirk_apple_poweroff_thunderbolt()` does not help: Cactus Ridge 4C only, suspend-late only, and this
  firmware has no `SXIO`/`SXLV`.
- Root port 00:1c.4 needs Link Disable set and the thunderbolt module unloaded first.
- The FaceTime camera (14e4:1570) also needs ASPM L1 forced, otherwise `pc6` stays 0.
- Idle total system power (SMC PSTR): ~9.0 W -> ~6.2 W; `pc6` 0% -> ~65%; CPU package 2.5 W -> 1.2 W.
- After resume the root port link comes back enabled, so a sleep hook has to re-apply it.

Scripts, ACPI notes, and a diagnosis recipe: <REPO-URL>. Happy to turn this into a PR with an `mba72` section if you
want it here, or to keep it separate and link back. Results are from one machine so far.
