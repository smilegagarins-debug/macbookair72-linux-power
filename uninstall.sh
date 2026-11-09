#!/bin/bash
# Revert everything install.sh did (Thunderbolt power is restored first).
[ "$(id -u)" = 0 ] || { echo "run as root: sudo $0"; exit 1; }
systemctl disable --now mac-powerfix.service 2>/dev/null   # ExecStop runs `mac-powerfix revert`
rm -f /usr/lib/systemd/system-sleep/mac-powerfix /etc/systemd/system/mac-powerfix.service \
      /usr/local/sbin/mac-tbpower /usr/local/sbin/mac-powerfix /etc/modules-load.d/acpi_call.conf
systemctl daemon-reload
echo "Removed. (acpi-call-dkms left installed; remove with: apt purge acpi-call-dkms)"
