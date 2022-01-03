from io import BytesIO
from numpy.testing import assert_almost_equal
import pytest

from gnss.rtcm.messages import RtcmMessage
from gnss.rtcm.messages import (
    ReferenceStationAntenna, ReferenceStationAntennaHeight,
    ReceiverAntennaDescriptor
)


def test_ref_antenna():
    buff = bytes(b'>\xd0\x00\x026\xab\x10_\xca\x085\r\xd0\xca7\xe5G\xf8\x88\x00\x00')
    msg = ReferenceStationAntenna(buff=buff)

    assert msg.station_id == 0
    assert msg.gps_indicator
    assert not msg.glonass_indicator
    assert not msg.galileo_indicator
    assert not msg.station_indicator
    assert_almost_equal(msg.ecef_x, -4007969.5926, decimal=4)
    assert not msg.oscillator_indicator
    assert_almost_equal(msg.ecef_y, 3524983.62340, decimal=4)
    assert msg.quarter_cycle_indicator == 0
    assert_almost_equal(msg.ecef_z, -3480800.6520, decimal=4)


def test_ref_antenna_height():
    buff = bytes(b'>\xe0\x00\x026\xab\x10_\xca\x085\r\xd0\xca7\xe5G\xf8\x88\x00\x00')
    msg = ReferenceStationAntennaHeight(buff=buff)

    assert msg.station_id == 0
    assert msg.gps_indicator
    assert not msg.glonass_indicator
    assert not msg.galileo_indicator
    assert not msg.station_indicator
    assert_almost_equal(msg.ecef_x, -4007969.5926, decimal=4)
    assert not msg.oscillator_indicator
    assert_almost_equal(msg.ecef_y, 3524983.62340, decimal=4)
    assert msg.quarter_cycle_indicator == 0
    assert_almost_equal(msg.ecef_z, -3480800.6520, decimal=4)
    assert msg.height == 0


@pytest.mark.skip(reason="no implemented")
def test_receiver_antenna_descriptor():
    buff = bytes(b'@\x90\x00\x00\x00\x00\x08TPS OEM1\x124.7 Nov,23,2017 p6\x00')
    msg = ReceiverAntennaDescriptor(buff=buff)
