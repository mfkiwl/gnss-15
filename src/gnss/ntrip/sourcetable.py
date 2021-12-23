from urllib.parse import quote


STR_HEADERS = ("type", "mountpoint", "identifier", "format", "format-details",
               "carrier", "nav-system", "network", "country", "latitude",
               "longitude", "nmea", "solution", "generator", "compression",
               "authentication", "fee", "bitrate", "misc")

NET_HEADERS = ("type", "identifier", "operator", "authentication", "fee",
               "web-net", "web-str", "web-reg", "misc")

CAS_HEADERS = ("type", "host", "port", "identifier", "operator", "nmea",
               "country", "latitude", "longitude", "fallback_host",
               "fallback_ip", "misc")


def get_headers(type_):
    if type_ == "CAS":
        headers = CAS_HEADERS
    elif type_ == "NET":
        headers = NET_HEADERS
    elif type_ == "STR":
        headers = STR_HEADERS
    else:
        raise ValueError('invalid type')
    return headers


def query_to_string(query: dict):
    query_strings = []
    for key, value in query.items():
        if key in ["auth", "strict"]:
            if value:
                query_strings.append(f"{key}=1")

        if key in ["match", "filter"]:
            type_ = value['type']
            filter_strings = []
            for header in get_headers(type_):
                if header in value:
                    filter_strings.append(quote(value[header]))
                else:
                    filter_strings.append("")
            filter_string = ";".join(filter_strings)
            query_strings.append(f"{key}={filter_string}")
    return "&".join(query_strings).rstrip(";")
