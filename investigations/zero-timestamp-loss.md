# PSLab PR #320: zero timestamp investigation

Inspected Python PR head `19478233e5a828b64ad25a0390a4d7a674dc28cc` and
firmware head `33b0b136b826fe30f59b177bb6f6ddf105cbcce4`.

## Verified behavior

The real `LogicAnalyzer._fetch_long()` method loses captured zeros at either
end of the data. A mocked transport supplies the same packed bytes as the
firmware's long-buffer response; no capture or fetch method is mocked.

| Captured timestamps (timer ticks) | Returned timestamps |
| --- | --- |
| `[0, 10240]` | `[10240]` |
| `[4294957056, 0]` | `[4294957056]` |
| `[100, 10340]` | `[100, 10340]` |

Run `python -m investigations.zero_timestamp_reproduction` from the repository
root with PSLab dependencies installed. The reproduction exits nonzero for the two losses. All 44 existing
hardware-free pulse-count cases pass at this head. Device integration tests
were not run; no device is attached.

## Why a progress-based Python patch is not ready

`_fetch_long()` trims leading and trailing zeros. Merely retaining every zero
would turn unused, cleared buffer space into apparent captured events.
A one-event capture ending in unused zeros and a two-event capture whose second
timestamp is zero can have identical buffer bytes.

The firmware's `INTERVAL_GetState()` sends the buffer base and `DMA0STAL`
through `DMA3STAL`. Its DMA helpers identify these as start addresses and
initialize them when preparing the capture. This source inspection does not
establish that the response is a reliable live event count. The Python decoder
also converts a zero offset to a full buffer, so substituting `get_progress()`
without verifying hardware behavior is unsafe.

Before changing the fetch path, verify the progress response on supported
hardware for no events, one event, partial and full buffers, and both halves
of a 32-bit timestamp. If the protocol cannot distinguish those states, a
firmware/protocol extension is needed. Any later Python patch must preserve
zeros only within a verified captured prefix and cover partial DMA writes and
capture continuing during retrieval.

No speculative patch or failing test was pushed to the existing PR.

Sources:

- [Current PR](https://github.com/fossasia/pslab-python/pull/320)
- [Python fetch and progress implementation](https://github.com/fossasia/pslab-python/blob/19478233e5a828b64ad25a0390a4d7a674dc28cc/pslab/instrument/logic_analyzer.py)
- [Firmware progress response](https://github.com/fossasia/pslab-firmware/blob/33b0b136b826fe30f59b177bb6f6ddf105cbcce4/src/helpers/interval.c)
- [Firmware DMA setup](https://github.com/fossasia/pslab-firmware/blob/33b0b136b826fe30f59b177bb6f6ddf105cbcce4/src/registers/memory/dma.c)
