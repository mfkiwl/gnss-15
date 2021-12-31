from enum import IntEnum
from bitstring import ConstBitStream


class Type(IntEnum):
    EXTENDED_L1_L2_GPS = 1004
    REFERENCE_STATION_ANTENNA = 1005
    REFERENCE_STATION_ANTENNA_HEIGHT = 1006
    ANTENNA_DESCRIPTOR = 1007
    EXTENDED_L1_L2_GLONASS = 1012
    SYSTEM_PARAMETERS = 1013

    GPS_IONOSPHERIC = 1015
    GPS_GEOMETRIC = 1016
    GPS_GEOMETRIC_INOSPHERIC = 1017
    GPS_EPHEMERIDES = 1019
    GLONASS_EPHEMERIDES = 1020

    UNICODE_TEXT_STRING = 1020
    RECEIVER_ANTENNA_DESCRIPTOR = 1033

    GALILEO_EPHEMERIS = 1045

    SSR_GPS_ORBIT = 1057
    SSR_GPS_CLOCK = 1058
    SSR_GPS_CODE_BIAS = 1059
    SSR_GPS_ORBIT_CLOCK = 1060
    SSR_GPS_URA = 1061
    SSR_GPS_RATE_CLOCK = 1062

    SSR_GLONASS_ORBIT = 1063
    SSR_GLONASS_CLOCK = 1064
    SSR_GLONASS_CODE_BIAS = 1065
    SSR_GLONASS_ORBIT_CLOCK = 1066
    SSR_GLONASS_URA = 1067
    SSR_GLONASS_RATE_CLOCK = 1068

    GPS_MSM1 = 1071
    GPS_MSM2 = 1072
    GPS_MSM3 = 1073
    GPS_MSM4 = 1074
    GPS_MSM5 = 1075
    GPS_MSM6 = 1076
    GPS_MSM7 = 1077

    GLONASS_MSM1 = 1081
    GLONASS_MSM2 = 1082
    GLONASS_MSM3 = 1083
    GLONASS_MSM4 = 1084
    GLONASS_MSM5 = 1085
    GLONASS_MSM6 = 1086
    GLONASS_MSM7 = 1087

    GALILEO_MSM1 = 1091
    GALILEO_MSM2 = 1092
    GALILEO_MSM3 = 1093
    GALILEO_MSM4 = 1094
    GALILEO_MSM5 = 1095
    GALILEO_MSM6 = 1096
    GALILEO_MSM7 = 1097

    QZSS_MSM1 = 1111
    QZSS_MSM2 = 1112
    QZSS_MSM3 = 1113
    QZSS_MSM4 = 1114
    QZSS_MSM5 = 1115
    QZSS_MSM6 = 1116
    QZSS_MSM7 = 1117

    BEIDOU_MSM1 = 1121
    BEIDOU_MSM2 = 1122
    BEIDOU_MSM3 = 1123
    BEIDOU_MSM4 = 1124
    BEIDOU_MSM5 = 1125
    BEIDOU_MSM6 = 1126
    BEIDOU_MSM7 = 1127

    GLONASS_L1_2_CODE_PHASE_BIASES = 1230


class RtcmMessage:
    _registry = {}
    _required_methods = ('from_buffer', 'to_buffer')

    def __init_subclass__(cls, msg_type: Type, **kwargs):
        super().__init_subclass__(**kwargs)
        for required_method in cls._required_methods:
            if hasattr(super(cls, cls), required_method):
                subclass_method = getattr(cls, required_method)
                parentclass_method = getattr(RtcmMessage, required_method)
                if subclass_method == parentclass_method:
                    raise NotImplementedError(
                        (f"method {required_method} "
                         + f"is not override by {cls.__name__}"))
            elif not hasattr(cls, required_method):
                raise NotImplementedError(
                    (f"method {required_method} "
                     + f"is not implemented in {cls.__name__}"))

        cls._registry[msg_type] = cls
        cls.type = msg_type

    def __new__(cls, msg_type: Type = None, **kwargs):
        if msg_type is not None:
            if msg_type in cls._registry:
                subclass = cls._registry[msg_type]
                instance = object.__new__(subclass)
            else:
                raise NotImplementedError(
                    f"message {msg_type} is not implemented")
        else:
            instance = object.__new__(cls)

        return instance

    def __init__(self, **kwargs):
        pass

    def from_buffer(self, buff: bytes):
        raise NotImplementedError

    def to_buffer(self, buff: bytes):
        raise NotImplementedError

    @classmethod
    def get_types(cls):
        return list(cls._registry.keys())

    @classmethod
    def get_class(cls, msg_type: Type):
        if msg_type not in cls._registry:
            raise NotImplementedError('message not implemented')
        return cls._registry[msg_type]

    @classmethod
    def get_name(cls, msg_type: Type):
        return cls.get_class(msg_type).__name__

    @property
    def name(self):
        return self.get_name(self.type)


class GpsRtkHeader:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.station_id = None
        self.gps_epoch = None
        self.synchronous_gnss = None
        self.nr_gps_sat = None
        self.divergence_free_smothing = None
        self.smothing_interval = None

    def from_bit_stream(self, stream: ConstBitStream):
        self.station_id = stream.read('uint:12')
        self.gps_epoch = stream.read('uint:30')
        self.synchronous_gnss = bool(stream.read('uint:1'))
        self.nr_gps_sat = stream.read('uint:5')
        self.divergence_free_smoothing = bool(stream.read('uint:1'))
        self.smoothing_interval = stream.read('uint:3')


class ExtendedL1L2Gps(
        RtcmMessage, GpsRtkHeader,
        msg_type=Type.EXTENDED_L1_L2_GPS,
        ):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sat_id = None
        self.l1_code_indicator = None
        self.l1_pseudorange = None
        self.l1_phaserange = None
        self.lock_time_indicator = None

    def from_buffer(self, buff: bytes):
        stream = ConstBitStream(buff)
        msg_number = Type(stream.read('uint:12'))
        if msg_number != self.type:
            raise RuntimeError('invalid message number received')

        super().from_bit_stream(stream)
        self.sat_id = stream.read('uint:6')
        self.l1_code_indicator = stream.read('uint:1')
        self.l1_pseudorange = stream.read('uint:24')
        self.l1_phaserange = stream.read('int:20') + self.l1_pseudorange
        self.lock_time_indicator = stream.read('uint:7')

    def to_buffer(self):
        raise NotImplementedError


class BaseAntenna:
    def __init__(self, **kwargs):
        self.station_id = None
        self.gps_indicator = None
        self.glonass_indicator = None
        self.galileo_indicator = None
        self.station_indicator = None
        self.ecef_x = None
        self.oscillator_indicator = None
        self.ecef_y = None
        self.quater_cycle_indicator = None
        self.ecef_z = None

    def from_stream(self, stream):
        self.station_id = stream.read('uint:12')
        stream.read('uint:6')
        self.gps_indicator = bool(stream.read('uint:1'))
        self.glonass_indicator = bool(stream.read('uint:1'))
        self.galileo_indicator = bool(stream.read('uint:1'))
        self.station_indicator = bool(stream.read('uint:1'))
        self.ecef_x = stream.read('int:38') * 1e-4
        self.oscillator_indicator = bool(stream.read('uint:1'))
        stream.read('uint:1')
        self.ecef_y = stream.read('int:38') * 1e-4
        self.quater_cycle_indicator = stream.read('uint:2')
        self.ecef_z = stream.read('int:38') * 1e-4


class ReferenceStationAntenna(
        RtcmMessage,
        BaseAntenna,
        msg_type=Type.REFERENCE_STATION_ANTENNA
        ):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def from_buffer(self, buff: bytes):
        stream = ConstBitStream(buff)
        msg_number = Type(stream.read('uint:12'))
        if msg_number != self.type:
            raise RuntimeError('invalid message number received')

        super().from_stream(stream)

    def to_buffer(self):
        raise NotImplementedError


class ReferenceStationAntennaHeight(
        RtcmMessage,
        BaseAntenna,
        msg_type=Type.REFERENCE_STATION_ANTENNA_HEIGHT
        ):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = None

    def from_buffer(self, buff: bytes):
        stream = ConstBitStream(buff)
        msg_number = Type(stream.read('uint:12'))
        if msg_number != self.type:
            raise RuntimeError('invalid message number received')

        super().from_stream(stream)
        self.height = stream.read('uint:16')

    def to_buffer(self):
        raise NotImplementedError


class GpsEphemeris(RtcmMessage, msg_type=Type.GPS_EPHEMERIDES):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def from_buffer(self, buff: bytes):
        raise NotImplementedError

    def to_buffer(self):
        raise NotImplementedError


class AntennaDescriptor(RtcmMessage, msg_type=Type.ANTENNA_DESCRIPTOR):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def from_buffer(self, buff: bytes):
        raise NotImplementedError

    def to_buffer(self):
        raise NotImplementedError


class ExtendedL1l2Glonass(RtcmMessage, msg_type=Type.EXTENDED_L1_L2_GLONASS):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def from_buffer(self, buff: bytes):
        raise NotImplementedError

    def to_buffer(self):
        raise NotImplementedError


class SystemParameters(RtcmMessage, msg_type=Type.SYSTEM_PARAMETERS):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def from_buffer(self, buff: bytes):
        raise NotImplementedError

    def to_buffer(self):
        raise NotImplementedError


class GpsInospheric(RtcmMessage, msg_type=Type.GPS_IONOSPHERIC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def from_buffer(self, buff: bytes):
        raise NotImplementedError

    def to_buffer(self):
        raise NotImplementedError


class GpsGeometric(RtcmMessage, msg_type=Type.GPS_GEOMETRIC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def from_buffer(self, buff: bytes):
        raise NotImplementedError

    def to_buffer(self):
        raise NotImplementedError


class GpsGeometricIonospheric(
        RtcmMessage,
        msg_type=Type.GPS_GEOMETRIC_INOSPHERIC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def from_buffer(self, buff: bytes):
        raise NotImplementedError

    def to_buffer(self):
        raise NotImplementedError
