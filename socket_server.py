import socketserver
import rsa
import socket
import celery

from base64 import b64encode, b64decode
from rsasigner import rsatn

class Handler_TCPServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("{} sent:".format(self.client_address[0]))
        print(self.data)
        token_crypto = str(self.data)
        results = str(rsatn("ADMIN", token_crypto))
        self.request.sendall(results.encode())

if __name__ == "__main__":
    HOST, PORT = "localhost", 9948
    tcp_server = socketserver.TCPServer((HOST, PORT), Handler_TCPServer)
    tcp_server.serve_forever()
