import pytest

from gnss.ntrip.sourcetable import STR_HEADERS, NET_HEADERS, CAS_HEADERS
from gnss.ntrip.sourcetable import get_headers, query_to_string


@pytest.mark.parametrize(
    "type_, headers",
    [("CAS", CAS_HEADERS),
     ("NET", NET_HEADERS),
     ("STR", STR_HEADERS),
     pytest.param("unknown", [], marks=pytest.mark.xfail(reason=ValueError))])
def test_get_headers(type_, headers):
    computed_headers = get_headers(type_)
    assert computed_headers == headers


@pytest.mark.parametrize(
    "query, string",
    [({}, ""),
     ({"auth": True}, "auth=1"),
     ({"auth": 1}, "auth=1"),
     ({"auth": "=1"}, "auth=1"),
     ({"auth": False}, ""),
     ({"auth": 0}, ""),
     ({"strict": True}, "strict=1"),
     ({"strict": 1}, "strict=1"),
     ({"strict": "=1"}, "strict=1"),
     ({"strict": False}, ""),
     ({"strict": 0}, ""),
     ({"auth": True, "strict": True}, "auth=1&strict=1"),
     ({"match": {"type": "CAS", "country": "test"}}, "match=CAS;;;;;;test"),
     ({"filter": {"type": "CAS", "latitude": ">=0"}},
      "filter=CAS;;;;;;;%3E%3D0"),
     ({"filter": {"type": "CAS", "latitude": ">=0", "longitude": ">=0"}},
      "filter=CAS;;;;;;;%3E%3D0;%3E%3D0"),
     ({"filter": {"type": "CAS", "latitude": ">=0+<=90", "longitude": ">=0"}},
      "filter=CAS;;;;;;;%3E%3D0%2B%3C%3D90;%3E%3D0"),
     ({"auth": True, "filter": {"type": "CAS", "latitude": ">=0"}},
      "auth=1&filter=CAS;;;;;;;%3E%3D0"),
     ({"strict": True, "filter": {"type": "CAS", "latitude": ">=0"}},
      "strict=1&filter=CAS;;;;;;;%3E%3D0"),
     ({"filter": {"type": "CAS", "country": "test"}}, "filter=CAS;;;;;;test")])
def test_query_to_string(query, string):
    computed_string = query_to_string(query)
    assert computed_string == string
