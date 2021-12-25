from io import BytesIO

import pytest

from gnss.rtcm.parser import Parser, PREAMBLE

def test_parse_garbage():
    stream = BytesIO()
    stream.write(b"0x561516515165e1d5a651d61512615a156117511479526205181684a13846f11d")
    stream.seek(0)

    parser = Parser(stream)

    parser.parse()

    assert not parser._issync

def test_parse_preamble():
    stream = BytesIO()
    stream.write(bytes([0x01, 0x02, PREAMBLE, 0x03, 0x01, 0x02, 0x03]))
    stream.seek(0)

    parser = Parser(stream)

    parser.parse()

    assert parser._issync
