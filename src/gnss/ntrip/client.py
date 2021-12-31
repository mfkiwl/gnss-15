import pandas as pd
from base64 import b64encode
import requests

from .sourcetable import get_headers, query_to_string


class Client:
    def __init__(
            self,
            caster_url: str,
            mountpoint: str = "",
            port: int = 2101,
            username: str = None,
            password: str = None,
            user_agent: str = "ntrip-client",
            ntrip_version: str = "2.0",
            ssl: bool = False,
            timeout=10,
            outstream=None,
            nmea: str = None,
            ):
        self.caster_url = caster_url
        self.mountpoint = mountpoint
        self.port = port
        self.timeout = timeout
        self.ssl = ssl
        self.outstream = outstream

        self.headers = {"Ntrip-Version": f"Ntrip/{ntrip_version}",
                        "User-Agent": user_agent,
                        "Connection": "close"}

        if username is not None:
            if password is None:
                raise ValueError('missing password')
            auth = b64encode(f"{username}:{password}".encode('utf-8'))
            self.headers["Authorization"] = "Basic " + auth.decode('utf-8')

        if nmea is not None:
            self.headers['Ntrip-GGA'] = nmea

        self.response = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        return f"Ntripclient: {self.caster_url}:{self.port}/{self.mountpoint}"

    def get_sourcetable(self, query: dict = None) -> pd.DataFrame:
        url = f"{self.caster_url}:{self.port}"
        params = query_to_string(query) if query is not None else ""
        sourcetable = pd.DataFrame()
        with requests.get(
                url,
                timeout=self.timeout,
                headers=self.headers,
                verify=self.ssl,
                params=params) as resp:
            resp.raise_for_status()
            if "Content-Type" in resp.headers:
                if resp.headers["Content-Type"] != "gnss/sourcetable":
                    raise RuntimeError(
                        "invalid content-type: "
                        f"{resp.headers['Content-Type']}")
            else:
                raise RuntimeError("unable to find Content-Type")

            for line in resp.iter_lines():
                line = line.decode("utf-8")
                values = line.split(";")
                try:
                    headers = get_headers(values[0])
                except ValueError:
                    if values[0] == "ENDSOURCETABLE":
                        break
                    else:
                        RuntimeError("invalid sourcetable")
                sourcetable = sourcetable.append(
                    dict(zip(headers, values)),
                    ignore_index=True)
        return sourcetable

    def get_data(
            self,
            nrbytes: int,
            mountpoint: str = None,
            timeout=None):
        if mountpoint is not None:
            if mountpoint != self.mountpoint:
                self.close()
                self.mountpoint = mountpoint

        if timeout is not None:
            if self.timeout != self.timeout:
                self.timeout = timeout
                self.close()

        if self.isclosed():
            self.connect()

        data = self.response.raw.read(nrbytes)
        if self.outstream is not None:
            self.outstream.write(data)
        return data

    def read(self, nrbytes: int):
        return self.get_data(nrbytes)

    def connect(self):
        url = f"{self.caster_url}:{self.port}/{self.mountpoint}"
        self.response = requests.get(
            url,
            headers=self.headers,
            stream=True,
            verify=self.ssl,
            timeout=self.timeout)
        if self.response.headers["Content-Type"] != "gnss/data":
            if self.response.headers["Content-Type"] == "gnss/sourcetable":
                raise ValueError("Invalid mountpoint")
            else:
                raise RuntimeError(
                    "invalid content-type: "
                    f"{self.response.headers['Content-Type']}")

    def close(self):
        if not self.isclosed():
            self.response.close()

    def isclosed(self):
        if self.response is None:
            return True
        elif self.response.raw is None:
            return True
        elif self.response.raw.isclosed():
            return True
        else:
            return False
