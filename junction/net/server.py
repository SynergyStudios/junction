import socket
from time import sleep as wait
from threading import Thread

from connection import Connection
from packet import Packet

WAIT_TIME = 0.1 # Synchronises threads

class Server:

    """A server object, which allows multiple clients to connect
       to each other and send packets to seach other."""

    def __init__(self, host_name: str, port: int):

        # Define server
        self.IP = socket.gethostbyname(host_name)
        self.Port = port

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connections = []

        self.state = True

        # Buffers
        self.main_buffer = {}
        self.archive_buffer = []

        # Flags
        self.prints = True
        self.warnings = False

    def send_to_all(self, packet: Packet):

        """Sends a packet as a broadcast."""

        for conn in self._connections:

            # Check connected
            if conn.connected:
                conn.send(packet)
    
    def send_to_all_except(self, packet: Packet, excluded: list):

        """Sends to all connections except a single connection."""

        all_connections = self._connections
        all_connections.remove(excluded)

        self.send_to_clients(all_connections)

    def send_to_client(self, packet: Packet, conn: Connection):

        """Send a packet to a specific connection."""

        # Check connected
        if conn.connected:
            conn.send(packet)

    def send_to_clients(self, packet: Packet, connections: list):

        """Sends a packet to a group of connections."""

        for conn in connections:

            # Check connected
            if conn.connected:
                conn.send(packet)

    def start(self):

        """Starts the server."""

        self.state = '#running'
        
        # Bind socket
        self._socket.bind((self.IP, self.Port))
        self._socket.listen()

        if self.prints:
            print(f'Server Socket Started at: {self.IP}, {self.Port}')

        self._loop()

    def stop(self):

        """Stops the server."""

        self.state = '#stopped'
        
        for conn in self._connections:

            # Check connected, disconnect
            if conn.connected:
                conn.disconnect()

        # Shutdown socket
        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

        self.state = '#shutdown'

        if self.prints:
            print(f'Server Socket Stopped.')

    def translate_packet(self, header, data, conn: Connection):

        """Translates the packet.
           Override this method to follow instructions differently."""

        #/example
        pass


    def _handle_client(self, conn: Connection):

        """Handles the client and translates instructions.
           Override this method to take instructions from the buffer
           and to do things with it."""

        socket_id = str(conn._socket)

        while conn.connected:
        
            if len(self.main_buffer[socket_id]) > 0:

                oldest_packet = self.main_buffer[socket_id][0]

                # Translate packet
                self.translate_packet(oldest_packet.header, oldest_packet.data, conn)

                if self.prints:
                    print(f'Packet received: {oldest_packet.header} : {oldest_packet.data}')

                self.main_buffer[socket_id].remove(oldest_packet)
                
                # Add to archive
                self.archive_buffer.append(oldest_packet)

    def _add_socket(self, sock: socket, addr):

        """Adds a socket to the list."""

        # Add to client list
        new_conn = Connection(sock)
        self._connections.append(new_conn)
        new_conn.connected = True

        if self.prints:
            print(f'New Conn: {str(sock)}')

        return new_conn
     
    def _loop(self):

        """The main server loop."""

        while self.state == '#running':
            
            # Accept new clients

            try:
                sock, info = self._socket.accept()
                conn = self._add_socket(sock, info)

                new_thread = Thread(target = self._handle_client, args = (conn,), name = f'ClientThread-{self._connections.index(conn)}', daemon = True)
                new_thread.start()

                self.main_buffer[str(conn._socket)] = []

                connection_thread = Thread(target = conn._listen, args = (self.main_buffer[str(conn._socket)],), name = f'ConnectionThread-{self._connections.index(conn)}', daemon = True)
                connection_thread.start()
                
            except ConnectionResetError:
                continue

s = Server('0.0.0.0', 6868)
s.start()
