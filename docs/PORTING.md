# Porting to another Mac

Untested outside MacBookAir7,2. Numbers that are model-specific:

| What | Air 7,2 | How to find |
|---|---|---|
| Root port | `00:1c.4` (`\_SB.PCI0.RP05`) | `lspci -tv`, root port above the `DSL5320` bridge |
| Upstream bridge | `05:00.0` | next level in `lspci -tv` |
| NHI | `07:00.0` | `lspci -nn \| grep 0880` Thunderbolt NHI |
| ACPI path | `\_SB.PCI0.RP05.UPSB.DSB0.NHI0` | disassembled SSDT |
| Power methods | `SXFP(0)` off, `TRPE(1,100)` on | grep SSDTs for them |
| GPIO | GPIO47, pad register at I/O `0x978` | `GP47`/`GD47` in the method, then the PCH datasheet / `pinctrl` community offsets |
| Camera | Broadcom `14e4:1570` at `02:00.0` | `lspci -nn` |

Steps: (1) run docs/DIAGNOSE.md; (2) dump and disassemble tables, find the SSDT with the Thunderbolt power
methods; (3) try the method by hand with `acpi_call`
(`echo '\_SB.PCI0.RP05.UPSB.DSB0.NHI0.SXFP 0' | sudo tee /proc/acpi/call`, `cat /proc/acpi/call`),
watching `turbostat` and power; (4) adapt `RP`, `UP`, `NHI`, and the GPIO port in `scripts/mac-tbpower`.

Calling unknown ACPI methods can hang the machine. `sync` first, keep the power button in reach, start with
read-only methods (`_STA`).
