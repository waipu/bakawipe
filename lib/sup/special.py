from io import BytesIO
try:
    import simplejson as json
except ImportError:
    import json
try:
    import msgpack
    has_msgpack = True
except ImportError:
    has_msgpack = False

class SpecialBase(object):
    def __init__(self, *args, **kvargs):
        self.encoding = 'utf-8'

    def json(self, *args, **kvargs) -> object:
        "Try to parse json from self and return it"
        return json.loads(self, *args, **kvargs)

class SpecialBytes(SpecialBase, bytes):
    def decode(self, encoding=None, errors='strict') -> str:
        "bytes.decode with per-object default encoding"
        return bytes.decode(
            self, encoding if encoding else self.encoding,
            errors)

    def s_decode(self, encoding=None, errors='strict') -> SpecialBase:
        "Same as decode, but returns SpecialString"
        e = encoding if encoding else self.encoding
        s = SpecialString(bytes.decode(self, e, errors))
        s.encoding = e
        return s

    def msgpack(self, *args, **kvargs) -> object:
        if not has_msgpack:
            raise NotImplementedError('No msgpack library here')
        return msgpack.unpackb(self)

    def json(self, *args, **kvargs) -> object:
        return self.s_decode().json(*args, **kvargs)

class SpecialString(SpecialBase, str):
    def encode(self, encoding=None, errors='strict') -> bytes:
        "str.encode with per-object default encoding"
        return str.encode(
            self, encoding if encoding else self.encoding,
            errors)

    def s_encode(self, encoding=None, errors='strict') -> SpecialBase:
        "Same as encode, but returns SpecialBytes"
        e = encoding if encoding else self.encoding
        b = SpecialBytes(str.encode(self, e, errors))
        b.encoding = e
        return b

class SpecialBytesIO(BytesIO):
    def __init__(self, *args, **kvargs):
        self.encoding = 'utf-8'
        super().__init__(*args, **kvargs)

    def s_getvalue(self) -> SpecialBytes:
        s = SpecialBytes(self.getbuffer())
        s.encoding = self.encoding
        return s
