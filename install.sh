#!/bin/bash
# Install mac-powerfix on a MacBookAir7,2 running a Debian/Ubuntu-family distro.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "run as root: sudo $0"; exit 1; }
HERE=$(cd "$(dirname "$0")" && pwd)
MODEL=$(cat /sys/class/dmi/id/product_name 2>/dev/null || true)
if [ "$MODEL" != "MacBookAir7,2" ]; then
  echo "This was tested only on MacBookAir7,2 (detected: '$MODEL')."
  echo "PCI addresses and GPIO numbers are model-specific. Read docs/PORTING.md first."
  [ "${FORCE:-0}" = 1 ] || { echo "Set FORCE=1 to install anyway."; exit 1; }
fi
apt-get install -y acpi-call-dkms pciutils python3 linux-tools-common 2>/dev/null || apt-get install -y acpi-call-dkms pciutils python3
install -m 755 "$HERE/scripts/mac-tbpower" "$HERE/scripts/mac-powerfix" /usr/local/sbin/
install -m 644 "$HERE/systemd/mac-powerfix.service" /etc/systemd/system/
install -m 644 "$HERE/systemd/acpi_call.conf" /etc/modules-load.d/acpi_call.conf
install -D -m 755 "$HERE/systemd/mac-powerfix.sleep-hook" /usr/lib/systemd/system-sleep/mac-powerfix
modprobe acpi_call
systemctl daemon-reload
systemctl enable --now mac-powerfix.service
echo; /usr/local/sbin/mac-tbpower status
echo "Done. Revert: sudo ./uninstall.sh"
