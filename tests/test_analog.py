"""Hardware-free tests for analog waveform conversion."""

import numpy as np

from pslab.instrument.analog import AnalogOutput


def test_waveform_tables_normalize_voltage_endpoints():
    output = AnalogOutput("SI1")
    output.waveform_table = np.tile(np.repeat([-3.3, 3.3], 16), 16)

    assert output.waveform_table == np.tile(np.repeat([0, 511], 16), 16).tolist()
    assert output.lowres_waveform_table == [0, 63] * 16
