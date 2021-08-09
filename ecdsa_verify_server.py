import socketserver

from ecdsa_celery_daemon import dsavf

class handle_tcp(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(2048).strip()
        print("{} sent:".format(self.client_address[0]))
        print(self.data)
        results = str(dsavf(self.data))
        # Example implementing some functionality upon successful validation
        #validated = ;Valid entry found.'
        #if results == validated:
        #    do something
        self.request.sendall(results.encode())

if __name__ == "__main__":
    HOST, PORT = "localhost", 9849
    tcp_server = socketserver.TCPServer((HOST, PORT), handle_tcp)
    tcp_server.serve_forever()
