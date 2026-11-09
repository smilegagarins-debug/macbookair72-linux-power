# ACPI structure of the Thunderbolt power control (MacBookAir7,2)

Dumped with `acpidump` + `iasl -d` (acpica-tools). The relevant code is **SSDT "PcieTbt"**
(OEM ID `APPLE `, OEM Table ID `PcieTbt`, one of SSDT1-SSDT11 on this firmware; find it with
`grep -l PcieTbt *.dsl`). It is NOT in the DSDT, so `strings /sys/firmware/acpi/tables/DSDT`
shows no `SXIO`/`SXFP`/`SXLV`.

Full tables are firmware (c) Apple and are not redistributed here. Short excerpts for interoperability:

## Path

```
\_SB.PCI0.RP05                    root port 00:1c.4
  .UPSB                           05:00.0  Thunderbolt upstream bridge
    .DSB0                         06:00.0
      .NHI0                       07:00.0  Native Host Interface
        SXFP(Arg0)   power off when Arg0 == 0
        TRPE(Arg0, Arg1)  Arg0=0: link down + power off, Arg0=1: power on + train link (Arg1 = ms)
        XRST, XRIO, XRIP, XRIL   reset / force-power related, GPIO57 and GPIO77
```

## SXFP

```
Method (SXFP, 1, Serialized)
{
    If ((Arg0 == 0x00))
    {
        GP47 = 0x00      // GPIO47 output level low
        GD47 = 0x00      // GPIO47 direction: output
    }
}
```

GPIO47 of the Wildcat Point-LP PCH is the Thunderbolt controller's power-enable. Reading the pad
register (I/O port `0x978` = GPIO community base `0x800` + `0x100` + 47*8):

| value | meaning |
|---|---|
| `0x40000005` | input / powered (pull-up), controller on |
| `0x1`        | output low, controller unpowered |

## TRPE (power-on path, abridged)

```
Method (TRPE, 2, Serialized)
{
    If (OSDW ())                         // true when the OS answered _OSI("Darwin")
    {
        ...
        // Arg0 == 1: release GPIO47, clear LDIS (link disable) on RP05, wait for link, ...
    }
}
```

`OSDW()` is `1` under Linux because Linux answers `_OSI("Darwin")` on Apple hardware, so the
"Windows-only" branches in this table are not taken.

## Kernel quirk and why it does not apply

`drivers/pci/quirks.c: quirk_apple_poweroff_thunderbolt()` calls
`DSB0.NHI0.SXIO/SXFP/SXLV`, but
* registered via `DECLARE_PCI_FIXUP_SUSPEND_LATE`, only for `PCI_DEVICE_ID_INTEL_CACTUS_RIDGE_4C`
  (this Mac is Falcon Ridge 2C, `8086:156b` bridge / `8086:156a` NHI),
* only `if (pm_suspend_via_firmware())`,
* it returns unless all three methods exist; this firmware has `SXFP` and `TRPE`/`XRST`, not `SXIO`/`SXLV`.

It is a suspend-time helper, not a runtime power switch.
