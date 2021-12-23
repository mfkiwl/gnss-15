import pytest

from gnss.ntrip.client import Client
from gnss.ntrip.sourcetable import get_headers


@pytest.mark.parametrize(
    "username, password, auth",
    [("username", "password", "dXNlcm5hbWU6cGFzc3dvcmQ="),
     ("test_username", "test_passwd", "dGVzdF91c2VybmFtZTp0ZXN0X3Bhc3N3ZA==")])
def test_client_auth(username, password, auth):
    client = Client("test", username=username, password=password)
    assert client.headers["Authorization"] == f"Basic {auth}"


def test_get_sourcetable(requests_mock):
    FAKE_SOURCETABLE = "STR;ZUPT6818;Houston, Tx;RTCM 3.2;1005(1),1077(1),1087(1),1097(1),1127(1);;GPS+GLO+GAL+BDS;SNIP;USA;29.94;-95.53;1;0;sNTRIP;none;N;N;6800;\r\nSTR;zznrcstrk;Torak;RTCM 3.2;1005(5),1077(1),1087(1),1097(1),1230(1);;GPS+GLO+GAL;SNIP;SRB;45.51;20.60;1;0;sNTRIP;none;N;N;5720;\r\nNET;SNIP;RTK2go;N;N;rtk2go.com;rtk2go.com:2101;support@use-snip.com;;\r\nENDSOURCETABLE\r\n'"

    requests_mock.get(
        "mock://test.com:2101",
        headers={'Ntrip-Version': 'Ntrip/2.0',
                 'Content-Type': 'gnss/sourcetable',
                 'Connection': 'close',
                 'Content-Length': ''},
        text=FAKE_SOURCETABLE)
    client = Client("mock://test.com", port=2101)
    df = client.get_sourcetable()
    headers = get_headers('CAS') + get_headers('NET') + get_headers('STR')
    assert len(df) != 0
    assert all(col in headers for col in df.columns)


def test_get_data(requests_mock):
    FAKE_DATA = ",".join(["fake_data"] * 1024)
    requests_mock.get(
        "mock://test.com:2101/fake_data",
        headers={'Ntrip-Version': 'Ntrip/2.0',
                 'Content-Type': 'gnss/data',
                 'Connection': 'close',
                 'Content-Length': ''},
        text=FAKE_DATA)
    with Client("mock://test.com", mountpoint="fake_data", port=2101) as client:
        data = client.get_data(len(FAKE_DATA))
        assert data.decode("utf-8") == FAKE_DATA
