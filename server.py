#  coding: utf-8 
import socketserver
import os
from urllib.parse import urlparse
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

        if get_request == "GET" and self.check_directory(directory):
            self.do_GET(directory)
        elif (get_request == "POST" or get_request == "PUT" or get_request == "Delete"):
            self.request.sendall(bytes("HTTP/1.1 405 METHOD NOT ALLOWED\r\n\r\n","utf-8"))
            self.request.recv(1024).strip().decode("utf-8")
        elif get_request == "GET" and directory == "/deep":
            self.request.sendall(bytes("HTTP/1.1 301 Moved Permanently\r\nLocation: http://127.0.0.1:8080/deep/\r\n\r\n","utf-8"))
            self.request.recv(1024).strip().decode("utf-8")
        else:
            self.request.sendall(bytes("HTTP/1.1 404 NOT FOUND\r\n\r\n","utf-8"))
            self.request.recv(1024).strip().decode("utf-8")

    def do_GET(self, directory):
        path = "www/"
        html = "index.html"

        f = os.path.abspath(path + directory + html)
        sz = os.path.getsize(f)
        sz = str(sz)
        content = "Content-type: text/html; utf-8\r\n"
        status = "HTTP/1.1 200 OK\r\n"
        octet = "content-length: " + sz + "\r\n"
        connection = "Connection: close\r\n\r\n"

        file = open(f, "r")
        data = file.read()
        data = status + content + octet + connection + data
        self.request.sendall(bytes(data, "UTF-8"))
        self.request.recv(1024).strip().decode("utf-8")
        
    def check_directory(self, dir):
        path = "www/"
        directory = dir.split("/")
        if directory[len(directory)-1] == "" and os.path.isdir(os.path.abspath(path + dir)):
            return True
        else:
            return False


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
