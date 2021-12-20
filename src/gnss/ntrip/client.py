from base64 import b64encode
from htttplib import HTTPConnection, HTTPSConnection


class Client:
    def __init__(
            self,
            caster_hostname: str,
            port: int,
            mointpoint: str,
            out_stream=None,
            user_agent: str = "test",
            ssl: bool = False,
            gga: str = None,
            latitude: float = None,
            longitude: float = None
            ):
        pass

    def __del__(self):
        self.disconnect()

    def connect(self):
        pass

    def disconnect(self):
        pass

    @classmethod
    def get_sourcetable(cls, caster_hostname: str, port: int) -> dict:
        pass

    def read(self):
        pass

    def to_stream(self, outstream):
        pass
