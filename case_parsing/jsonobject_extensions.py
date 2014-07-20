import base64
import iso8601
from jsonobject import JsonProperty, DateTimeProperty, JsonObject


class Base64Property(JsonProperty):
    def unwrap(self, obj):
        return obj, base64.decodestring(obj)

    def wrap(self, obj):
        return base64.encodestring(obj)


class ISO8601Property(DateTimeProperty):
    def __init__(self, **kwargs):
        if 'exact' in kwargs:
            assert kwargs['exact'] is True
        kwargs['exact'] = True
        super(ISO8601Property, self).__init__(**kwargs)

    def wrap(self, obj):
        dt = iso8601.parse_date(obj)
        return dt.astimezone(iso8601.iso8601.UTC).replace(tzinfo=None)


class StrictJsonObject(JsonObject):
    _allow_dynamic_properties = False
    _string_conversions = ()
