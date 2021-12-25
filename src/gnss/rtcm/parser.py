from enum import IntEnum

from bitstring import ConstBitStream


PREAMBLE = 0xd3
BUFFER_SIZE = 2048

class Parser:
    def __init__(self, stream=None):
        self._callbacks = {}
        self.counts = {}
        self.error_count = 0
        self._msg = None
        self._end_of_stream = False
        self._issync = False
        self._buffer = bytearray()
        self.break_msg_types = []
        self.stream = stream

    def load_stream(self, stream):
        self.stream = stream

    def parse(self) -> None:
        """
        Parse RTCM binary messages.
        """
        while True:
            if len(self._buffer) < BUFFER_SIZE:
                buff = self.stream.read(BUFFER_SIZE)
                if not buff:
                    self._end_of_stream = True
                    break
                self._buffer += buff

            if not self._issync:
                for index, byte in enumerate(self._buffer):
                    self._issync = byte == PREAMBLE
                    if self._issync:
                        break
                self._buffer = self._buffer[index:]

            if self._issync:
                if len(self._buffer) <= 3:
                    continue

            stream = ConstBitStream(self._buffer[1:3])
            stream.pos += 14
            msg_length = stream.read('uint:10')

            if len(self._buffer) < (6 + msg_length):
                continue
            crc = self._buffer[3 + msg_length: 6 + msg_length]
            cmp_crc = self.compute_crc(self._buffer[: 3 + msg_length])
            if cmp_crc != crc:
                self._buffer = self._buffer[1:]
                self._issync = False
                continue

            self.parse_message(self._buffer[3: 3 + msg_length])
            self._buffer = self._buffer[6 + msg_length:]
            self.issync = False

            if self._msg.type in self.break_msg_types:
                break

    def compute_crc(self, buff: bytearray) -> bytearray:
        return bytearray("0x00")

    def parse_message(self, buff: bytearray) -> None:
        pass
