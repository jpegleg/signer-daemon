import socketserver
import rsa
import socket
import celery

from base64 import b64encode, b64decode
from rsasr import rsatn

class handle_tcp(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            self.data = self.request.recv(1024).strip()
        except Exception as error:
            results = error
        finally:
            print("{} sent:".format(self.client_address[0]))
            print(self.data)
            token_crypto = str(self.data)
            try:
                results = str(rsatn("RSA", token_crypto))
            except Exception as error:
                results2 = error
                results = results + results2
            finally:
                self.request.sendall(results.encode())

if __name__ == "__main__":
    HOST, PORT = "localhost", 9948
    tcp_server = socketserver.TCPServer((HOST, PORT), handle_tcp)
    tcp_server.serve_forever()
