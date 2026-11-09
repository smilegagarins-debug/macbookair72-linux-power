# Measurement protocol and data

Tool: `tools/pmeas.py LABEL SECONDS` (reads Apple SMC keys through ports 0x300/0x304, battery current x voltage, and
runs `turbostat` for the same window). `tools/smc.py` requires `applesmc` unloaded: `sudo modprobe -r applesmc`, then
`sudo modprobe applesmc` afterwards.

Why SMC `PSTR`: on this laptop the battery driver reports `current_now`/`voltage_now` but no `power_now`, and
the charger confuses readings. `PSTR` is total system power in watts and works on AC; `PDTR - PSTR` matches the
battery charge current.

Protocol: reboot, 10 minutes warm-up, fixed brightness, no browser, 3 pairs x 30 s, report mean and spread.
Accept an effect only if it exceeds spread.

| Series | Thunderbolt on | Thunderbolt off |
|---|---|---|
| Idle, 100% brightness | 8.83, 9.01, 9.18 | 6.61, 6.78, 5.29 |
| Screen off | 5.2-5.4 | 3.0 |
| Chrome open, CPU 13% | 11.1 | 9.1-9.6 |
| Brightness 100 / 50 / 10% (TB off) | 9.2-9.6 / 8.2 / 7.2 | |

## Not yet measured

- Discharging battery with video playback (battery hours with and without the fix). Expected, not measured:
  about -1.5 to -2 W with Chrome running.
- Behaviour on other Mac models.
