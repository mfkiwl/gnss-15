from io import BytesIO
import requests

from gnss.ntrip.client import Client
from gnss.rtcm.parser import Parser

parser = Parser()
with Client("http://rtk2go.com", port=2101, mountpoint="ACASU") as client:
    data = client.get_data(1024 * 10)
    stream = BytesIO(data)
    parser.load_stream(stream)
    parser.parse()
