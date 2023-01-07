import json
import socket

from base64 import b64encode, b64decode
from typing import Union

from packet import Packet

class Connection:

    """A connection object representing 
       a socket to another socket."""

    def __init__(self, sock):
        
        self._socket = sock
        # self._addr = addr

        self.name = None
        self.connected = False

        self.TERMINATOR = b"\0"
        self.CHUNK_SIZE = 1024

    def _close(self):

        """Closes the socket."""

        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

    def _packet_transformer(self, packet: Packet):

        """Transforms a packet into the correct format."""

        decoded_data = self._decode_data(packet.data)
        return Packet(packet.header, decoded_data)


    def _listen(self, buffer_dump):

        """Listens for messages on this client."""
        
        while self.connected:

            stream = b""

            while self.TERMINATOR not in stream:
        
                try:
                    stream += self._socket.recv(self.CHUNK_SIZE)

                except (ConnectionResetError, ConnectionError, ConnectionAbortedError, ConnectionRefusedError):
                    self._close()

                packet = Packet.decode(stream.split(self.TERMINATOR)[0])

                if packet.header == '/disconnect':
                    self._close()
                
                else:
                    transformed_packet = self._packet_transformer(packet)
                    buffer_dump.append(transformed_packet)

    def disconnect(self):

        """Disconects the connection."""

        self.connected = False
        self._close()

    @staticmethod
    def _encode_data(data: dict):
        return b64encode(json.dumps(data).encode("utf-8")).decode("utf-8")

    @staticmethod
    def _decode_data(encoded: Union[str, bytes]):
        return json.loads(b64decode(encoded))
    
    def send(self, packet: Packet):
        encoded_data = self._encode_data(packet.data)
        final_packet = Packet(packet.header, encoded_data)

        bytes_to_send = bytes(final_packet) + self.TERMINATOR

        size = len(bytes_to_send)
        current_chunks = 0

        while current_chunks < size:

            # Chunk data
            chunked_data = bytes_to_send[(current_chunks):(current_chunks) + self.CHUNK_SIZE]
            self._socket.send(chunked_data)
            current_chunks += self.CHUNK_SIZE