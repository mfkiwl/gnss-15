PREAMBLE = 0xd3

class State(IntEnum):
    """
    Parser state
    """
    NOSYNC = 0
    SYNC1 = 1
    MESSAGE = 2


class Parser:
    def __init__(self):
        self._callbacks = {}
        self.counts = {}
        self.error_count = 0
        self._msg = None
        self._end_of_stream = False
        self._state = State.NOSYNC
        self._buffer = bytearray()
        self.break_msg_ids = []

    def load_stream(self, stream):
        pass

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

            if self._state == State.NOSYNC:
                index = 0
                for byte in self._buffer:
                    index += 1
                    if byte == SYNC1:
                        self._state = State.SYNC1
                        break
                self._buffer = self._buffer[index:]

            if self._state == State.SYNC1:
                byte = self._buffer[0]
                if byte == SYNC2:
                    self._state = State.MESSAGE
                else:
                    self._state = State.NOSYNC
                    self.error_count += 1
                self._buffer = self._buffer[1:]

            if self._state == State.MESSAGE:
                if len(self._buffer) <= 4:
                    continue

                try:
                    msg_id = Id(self._buffer[0])
                    msg_class = Class(self._buffer[1])
                except ValueError:
                    self.error_count += 1
                    self._state = State.NOSYNC
                    continue

                try:
                    msg_name = SbgMessage.get_name(msg_id)
                    try:
                        self.counts[msg_name] += 1
                    except KeyError:
                        self.counts[msg_name] = 1
                except NotImplementedError:
                    self._state = State.NOSYNC
                    continue

                if msg_id not in self._required_msg_ids:
                    self._state = State.NOSYNC
                    continue

                payload_size = np.frombuffer(
                    self._buffer[2:4],
                    dtype=np.dtype(np.uint16).newbyteorder(self.endianness))[0]

                if payload_size > MAX_PAYLOAD_SIZE:
                    self.error_count += 1
                    self._state = State.NOSYNC
                    continue

                msg_size = 4 + payload_size + 2
                crc = np.frombuffer(
                    self._buffer[msg_size - 2:msg_size],
                    dtype=np.dtype(np.uint16).newbyteorder(self.endianness))[0]

                crc_computed = self._crc_fn(self._buffer[:msg_size - 2])

                if crc != crc_computed:
                    self.error_count += 1
                    self._state = State.NOSYNC
                    continue

                payload = self._buffer[4:payload_size + 4]
                self.parse_payload(msg_id, msg_class, payload)
                self._buffer = self._buffer[msg_size:]
                self._state = State.NOSYNC

                if msg_id in self._callbacks:
                    for callback in self._callbacks[msg_id]:
                        callback(self._msg)

                if self._msg.msg_id in self.break_msg_ids:
                    break


