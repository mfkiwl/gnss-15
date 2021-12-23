from enum import IntEnum


class Type(IntEnum):
    GPS_IONOSPHERIC = 1015
    GPS_GEOMETRIC = 1016
    GPS_EPHEMERIDES = 1019
    GLONASS_EPHEMERIDES = 1020

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
    _required_methods = ('frombuffer',)

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


class GpsEphemeris(RtcmMessage, msg_type=Type.GPS_EPHEMERIDES):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def frombuffer(self, buff):
        raise NotImplementedError
