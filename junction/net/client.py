import socket
from time import sleep as wait
from threading import Thread

from connection import Connection
from packet import Packet

WAIT_TIME = 0.1 # Synchronises threads

class Client:

    """A client object, which connects to a server and
       sends and receives packets to and from that server."""

    def __init__(self, ip: str, port: int):
        
        self.IP = socket.gethostbyname(ip)
        self.Port = port

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection = Connection(self._socket)

        self.state = None

        # Buffers
        self._buffer = []
        self.archive_buffer = []

        # Flags
        self.prints = True
        self.warnings = False

    def connect(self):

        """Connects the client to a server."""

        wait(WAIT_TIME)
        
        self._socket.connect((self.IP, self.Port))
        self._connection.connected = True
        # self._connnection = Connection(self._socket, self.IP)
        
        # Setup listening thread
        listen_thread = Thread(target = self._listen_for_client, args = (self._connection,), name = f'ListenThread-1', daemon = True)
        listen_thread.start()

        connection_thread = Thread(target = self._connection._listen, args = (self._buffer,), name = f'ListenThread-2', daemon = True)
        connection_thread.start()

        self.state = '#connected'

        if self.prints:
            print(f'Client Socket connected to {self.IP}, {self.Port}')
        
        self._loop()


    def disconnect(self):

        """Disconnects the client."""

        self._connection.disconnect()

        self.state = '#disconnected'

        if self.prints:
            print(f'Client socket disconnected!')


    def send(self, packet: Packet):

        """Sends a packet to the server."""

        self._connection.send(packet)

    def translate_packet(self, header, data):

        """Translates the packet.
           Override this method to follow instructions differently."""

        #/example
        pass


    def _listen_for_client(self, conn: Connection):

        """Listens for the client and translates instructions.
           Override this method to take instructions from the buffer
           and to do things with it."""

        if len(self._buffer) > 0:

            oldest_packet = self._buffer[-1]

            # Translate packet
            self.translate_packet(oldest_packet.header, oldest_packet.data)

            if self.prints:
                print(f'Packet received: {oldest_packet.header} : {oldest_packet.data}')

            self._buffer.remove(oldest_packet)

            # Add to archive
            self.archive_buffer.append(oldest_packet)

    def _loop(self):

        """The main client loop."""

        while self.state == '#connected':

                try:

                    # Do things here
                    self.tick()

                    wait(WAIT_TIME)

                except ConnectionResetError:
                    continue

    def tick(self):

        """A single rotation of the client loop."""

        pass

c = Client('127.0.0.1', 6868)
c.connect()