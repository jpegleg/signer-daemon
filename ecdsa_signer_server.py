import socketserver

from ecdsa_celery_daemon import dsatn

class handle_tcp(socketserver.BaseRequestHandler):
    def handle(self):
        """ listen for TCP connections and read 2048 bytes at a time """
        self.data = self.request.recv(2048).strip()
        print("{} sent:".format(self.client_address[0]))
        print(self.data)
        results = str(dsatn(self.data))
        self.request.sendall(results.encode())

if __name__ == "__main__":
    HOST, PORT = "localhost", 9848
    tcp_server = socketserver.TCPServer((HOST, PORT), handle_tcp)
    tcp_server.serve_forever()
