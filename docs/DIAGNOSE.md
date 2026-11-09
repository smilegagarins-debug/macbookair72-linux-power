# Is the package C-state ceiling your problem, too?

```
sudo apt install linux-tools-common linux-tools-$(uname -r)   # turbostat
sudo turbostat --quiet --show Busy%,Pkg%pc2,Pkg%pc3,Pkg%pc6,Pkg%pc7,PkgWatt,GFX%rc6 --interval 15 --num_iterations 1
```

On an idle desktop a healthy Broadwell-U shows large `Pkg%pc6`/`pc7`. If `pc6` and above are 0.00
while `pc3` is high (here: pc3 78%, pc2 9-13%), something keeps a PCIe link or device busy.

## Look for links without ASPM

```
sudo lspci -vv | awk '/^[0-9a-f:.]+ /{dev=$0} /LnkCtl:/{print substr(dev,1,60) " | " $0}' | grep ASPM
```

On MacBookAir7,2: `ASPM Disabled` on the Thunderbolt chain (`00:1c.4`, `05:00.0`, `06:*`, `07:00.0`) and on
the camera (`02:00.0`). SSD and Wi-Fi already have L1.

Test per device (temporary, reboot clears it):

```
echo 1 | sudo tee /sys/bus/pci/devices/0000:02:00.0/link/l1_aspm
```

Camera alone: about -0.5 W but pc6 stays 0. Thunderbolt could not be set to L1 (write accepted, stays 0).

## Find the ACPI power control

```
sudo apt install acpica-tools
mkdir acpi && cd acpi && sudo acpidump -b && iasl -d *.dat
grep -il "thunderbolt\|PcieTbt\|NHI0" *.dsl
```

Look for `SXIO`, `SXFP`, `SXLV`, `TRPE`, `XRST`, `_PS3`, `_PR3`, power resources under the root port that
leads to `DSL5320`/`DSL`-named Thunderbolt bridges (`lspci | grep -i thunderbolt`).

## Verify power is really gone

```
sudo mac-tbpower status        # GPIO47 pad value
```

Other checks: `lspci | grep -ci thunderbolt` drops to 0 (devices removed), RAPL package power falls,
`Pkg%pc6` rises.
