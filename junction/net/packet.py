from json import dumps, loads
from base64 import b64encode, b64decode

class Packet:

    """Singular packet of information with a header and data frame."""

    def __init__(self, header, data):

        self.ENCODING = 'utf-8'
        self.header = header
        self.data = data

        self.packet_info = {'to': None, # To add to dumped data
                            'from': None,
                            'timestamp': None}

    # Static decoding method
    @staticmethod
    def decode(encoded: bytes):
        decoded = loads(b64decode(encoded).decode('utf-8'))  # Temp removed self

        header = decoded['header']
        data = decoded['data']

        return Packet(header, data)

    def encoded(self):
        return bytes(self)

    def __bytes__(self):
        return b64encode(dumps({
        'header': self.header,
        'data': self.data}).encode(self.ENCODING))