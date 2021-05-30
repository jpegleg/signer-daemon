import socketserver
import rsa
import socket
import celery

from base64 import b64encode, b64decode
from rsa_celery_daemon import rsatn

class handle_tcp(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("{} sent:".format(self.client_address[0]))
        print(self.data)
        results = str(rsatn(self.data))
        self.request.sendall(results.encode())

if __name__ == "__main__":
    HOST, PORT = "localhost", 9948
    tcp_server = socketserver.TCPServer((HOST, PORT), handle_tcp)
    tcp_server.serve_forever()
