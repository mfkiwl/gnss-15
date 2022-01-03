from io import BytesIO
from numpy.testing import assert_almost_equal
import os

import pytest

from gnss.rtcm.parser import Parser, PREAMBLE
from gnss.rtcm.messages import ReferenceStationAntenna, ExtendedL1L2Gps


def test_parse_garbage():
    stream = BytesIO(
        b"0x561516515165e1d5a651d61512615a156117511479526205181684a13846f11d")
    parser = Parser(stream)
    parser.parse()


@pytest.mark.xfail(reason=RuntimeError)
def test_parse_preamble():
    stream = BytesIO(bytes([0x01, 0x02, PREAMBLE, 0x03, 0x01, 0x02, 0x03]))
    parser = Parser(stream)
    parser.parse()


def test_parse_msg():
    stream = BytesIO(
        b'\xd3\x00\xc4>\xc0\x00\x1d\xabVB\xc05\x00DH\x02\xe5\xff\xd1\xf0\x08'
        b'\x00 \x00\x03\xf8\x03\xcc\xe7\xe4\x00!\xaa\xfe\x87\x90\x7fB\x06\xd5'
        b'\x9f\xf0\x0ef\xb5\xa6\x82>\'\xf4\xab\x03\xf7O\xe5V\xff`\x91\xde\xd7'
        b'\xa3\xf1%\xff\xa8R\x1f\xc3\xfbR\x9f\xfaBA\x99\xb9\x7f\x92\xa7\xfdFp'
        b'\x00\xcf\xe9\xce\xff\xd28\x8c\xa9<\xffc\xa1i\xd2\x04\x00\x10\x00\x01'
        b'\xfc\x01\xb4-\x9e\x88\x01\xe2\xcfP\x94\x00(\x03\xce\x1f\x96\x03\x87'
        b'\xf8"\x7f$\x13\xfa>\x01\xf9\x8f\xf8\x9e\xff\xb0 H\x9f\xa9\xfa\x1f'
        b'\x9aT&\x00\x15@\x95\x1f\xfdb\x8e\rTO\xd1\xe6\xfe\x8dp@\x01\x00\x00'
        b'\x1f\xc0\x05\x06\xcc ~\xa6\xdf\xf4l\x03\xf4o\xc4\xcb\xffpy\xa6\xf5'
        b'\xef\xf17?\xa7\xd0\x1f\xb5\x81=\xfei@\xcbP\x0b')
    parser = Parser(stream)
    parser.parse()
    assert parser.error_count == 0


def test_parse_msg_reference_station_antenna():
    stream = BytesIO(bytes(
        [0xd3, 0x00, 0x13, 0x3e, 0xd7, 0xd3, 0x02, 0x02, 0x98, 0x0e, 0xde,
         0xef, 0x34, 0xb4, 0xbd, 0x62, 0xac, 0x09, 0x41, 0x98, 0x6f, 0x33,
         0x36, 0x0b, 0x98]))

    parser = Parser(stream)
    parser.parse()

    assert parser.error_count == 0

    assert isinstance(parser.msg, ReferenceStationAntenna)
    assert parser.msg.station_id == 2003
    assert_almost_equal(parser.msg.ecef_x, 1114104.5999, decimal=4)
    assert_almost_equal(parser.msg.ecef_y, -4850729.7108, decimal=4)
    assert_almost_equal(parser.msg.ecef_z, 3975521.4643, decimal=4)


def test_parser_callback():
    stream = BytesIO(bytes(
        [0xd3, 0x00, 0x13, 0x3e, 0xd7, 0xd3, 0x02, 0x02, 0x98, 0x0e, 0xde,
         0xef, 0x34, 0xb4, 0xbd, 0x62, 0xac, 0x09, 0x41, 0x98, 0x6f, 0x33,
         0x36, 0x0b, 0x98]))

    parser = Parser(stream)

    parsed_msgs = []

    @parser.callback
    def add_msg(msg: ReferenceStationAntenna):
        parsed_msgs.append(msg)

    parser.parse()

    assert parser.error_count == 0

    assert parser.msg.type == 1005
    assert parser.msg.station_id == 2003
    assert_almost_equal(parser.msg.ecef_x, 1114104.5999, decimal=4)
    assert_almost_equal(parser.msg.ecef_y, -4850729.7108, decimal=4)
    assert_almost_equal(parser.msg.ecef_z, 3975521.4643, decimal=4)

    assert len(parsed_msgs) == 1
    msg = parsed_msgs.pop()
    assert msg.type == 1005
    assert msg.station_id == 2003
    assert_almost_equal(msg.ecef_x, 1114104.5999, decimal=4)
    assert_almost_equal(msg.ecef_y, -4850729.7108, decimal=4)
    assert_almost_equal(msg.ecef_z, 3975521.4643, decimal=4)


def test_parse_rtcm_file():
    binary_file = os.path.join(os.path.dirname(__file__), 'rtcm_data.bin')
    with open(binary_file, 'rb') as stream:
        parser = Parser(stream)
        parser.parse()
    assert parser.error_count == 0


def test_iter_messages():
    binary_file = os.path.join(os.path.dirname(__file__), 'rtcm_data.bin')
    with open(binary_file, 'rb') as stream:
        parser = Parser(stream)
        for i, msg in enumerate(parser.iter_messages(ExtendedL1L2Gps)):
            assert isinstance(msg, ExtendedL1L2Gps)
    assert i == 6
    assert parser.counts[ExtendedL1L2Gps.get_name()] == i
    assert parser.error_count == 0
