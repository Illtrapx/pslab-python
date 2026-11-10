"""Reproduce timestamp loss without a PSLab device.

Run from the repository root in an environment with PSLab dependencies:
    python -m investigations.zero_timestamp_reproduction

Exit 1 means at least one captured timestamp was lost.
"""

from unittest.mock import Mock

import pslab.protocol as CP
from pslab.instrument.logic_analyzer import LogicAnalyzer


failed = 0
for captured in ([0, 10240], [2**32 - 10240, 0], [100, 10340]):
    raw = list(captured) + [0] * (CP.MAX_SAMPLES // 4 - len(captured))
    device = Mock()
    device.read.return_value = b"".join(CP.Integer.pack(value) for value in raw)
    analyzer = LogicAnalyzer(device)
    channel = analyzer._channels["LA1"]
    channel.buffer_idx = 0
    actual = analyzer._fetch_long(channel).tolist()
    passed = actual == captured
    failed += not passed
    print(f"{'PASS' if passed else 'FAIL'}: captured={captured}, fetched={actual}")

print(f"{failed} failing cases; 3 cases total")
raise SystemExit(bool(failed))
