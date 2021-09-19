#  coding: utf-8 
import socketserver
import os
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip().decode("utf-8")
        s = self.data.splitlines()
        block1 = s[0].split(" ")
        get_request = block1[0]
        directory = block1[1]

        if get_request == "GET" and (directory == "/" or directory == "/deep/"):
            if directory == "/":
                self.do_GET(1)
            elif directory == "/deep/":
                self.do_GET(2) 
        elif (get_request == "POST" or get_request == "PUT" or get_request == "Delete"):
            self.request.sendall(bytes("HTTP/1.1 405 METHOD NOT ALLOWED\n","utf-8"))
            self.request.recv(1024).strip().decode("utf-8")
        elif get_request == "GET" and directory == "/deep":
            self.request.sendall(bytes("HTTP/1.1 301 Moved Permanently\nLocation: http://127.0.0.1:8080/deep/\n","utf-8"))
            self.request.recv(1024).strip().decode("utf-8")
        else:
            self.request.sendall(bytes("HTTP/1.1 404 NOT FOUND\n","utf-8"))
            self.request.recv(1024).strip().decode("utf-8")

    def do_GET(self, depth):
        path = "www/"
        html = "index.html"
        deep_path = "www/deep/"

        content = "Content-type: text/html; utf-8\n"
        status = "HTTP/1.1 200 OK\n"

        if depth == 1 and os.path.exists(path + html):
            file = open(os.path.abspath(path + html), "r")
            data = file.read()
            data = status + content + data
            self.request.sendall(bytes(data, "UTF-8"))
            self.request.recv(1024).strip().decode("utf-8")

        elif depth == 2 and os.path.exists(deep_path + html):
            file = open(os.path.abspath(path + html), "r")
            data = file.read()
            data = status + content + data
            self.request.sendall(bytes(data, "UTF-8"))
            self.request.recv(1024).strip().decode("utf-8")


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
