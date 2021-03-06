import socketserver

from rsa_celery_daemon import rsavf

class handle_tcp(socketserver.BaseRequestHandler):
    def handle(self):
        """ listen for tcp connections and read 2048 bytes """
        self.data = self.request.recv(2048).strip()
        print("{} sent:".format(self.client_address[0]))
        print(self.data)
        results = str(rsavf(self.data))
        self.request.sendall(results.encode())

if __name__ == "__main__":
    HOST, PORT = "localhost", 9949
    tcp_server = socketserver.TCPServer((HOST, PORT), handle_tcp)
    tcp_server.serve_forever()
