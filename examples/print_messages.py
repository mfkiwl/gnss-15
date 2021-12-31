from io import BytesIO
import requests

from gnss.ntrip.client import Client
from gnss.rtcm.parser import Parser

parser = Parser()
with Client("http://rtk2go.com", port=2101, mountpoint="ACASU") as client:
    parser.load_stream(client, wait_for_stream=True)
    parser.parse()
