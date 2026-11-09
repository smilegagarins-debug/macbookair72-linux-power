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

- A full discharge test (hours to empty) with and without the fix. Hours in the README are computed from power x 53 Wh.
- Behaviour on other Mac models.

## Video playback on battery (2026-11-09)

Chrome playing H.264 video (VAAPI), brightness 50% (1401/2777), discharging, interleaved A-B-A:

| Series | PSTR per 30 s run (W) | mean | pc6 |
|---|---|---|---|
| A1 fix on | 7.17, 7.29, 7.38 | 7.28 | 27% |
| B fix off | 10.12, 9.27, 9.15 | 9.51 | 0% |
| A2 fix on | 7.15, 7.20, 7.53 | 7.29 | 29% |

Within-run std 0.5-2.4 W. Earlier single battery-current run at the same brightness: 6.39-6.58 W.
