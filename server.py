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
        block2 = s[1].split(": ")

        # components of the resquest, GET, directory/file and host
        get_request = block1[0]
        directory = block1[1]
        directory = "www" + directory
        host = block2[1]

        if "/../" in directory:
            self.Response(directory, host, "404")
        else:
            if get_request == "GET":
                #print("do_GET started")
                self.do_GET(directory, host)
            else:
                self.Response(directory, host, "405")
            
    def do_GET(self, directory, host):
        if self.check_directory(directory) == "301":
            self.Response(directory, host, "301")
        elif self.check_directory(directory) == "404":
            self.Response(directory, host, "404")
        elif self.check_directory(directory) == "file": # 200 OK, open file
            self.Response(directory, host, "file")
        elif self.check_directory(directory) == "directory": # 200 OK, read html by default
            self.Response(directory, host, "directory")
        
    def check_directory(self, directory):
        #print("check_directory started")
        # new list directory for 301 check purpose
        dir = directory.split("/")
        # checking to see if it end with /
        if dir[len(dir)-1] != "":
            # could be a file
            # checks to make sure IT IS a file
            if os.path.isfile(os.path.abspath(directory)):
                #print("it's a file")
                return "file"
            elif os.path.isdir(os.path.abspath(directory)):
                # it is an incompete directory
                #print("301")
                return "301"
            else:
                # file or directory just doesnt exist
                #print("404 first")
                return "404"
        else:
            # could be a directory
            # checks to make sure IT IS a directory with an index html
            if self.valid_directory(directory):
                #print("directory")
                return "directory"
            else:
                # has a slash but not index to be found
                #print("404 last")
                return "404"

    def valid_directory(self, directory):
        html = "index.html"
        # checks if it has index file in directory
        return os.path.isfile(os.path.abspath(directory + html))

    def Response(self, directory, host, status):
        html = "index.html"

        # not perfect, also issue of /.../.../ in inital stage
        if status == "301":
            protocol = "HTTP/1.1 301 Moved Permanently\r\n"
            Location = "Location: Http://" + host + "/" + "deep" + "/" + "\r\n"
            content = "Content-type: application/octet-stream; charset=UTF-8\r\n"
            connection = "Connection: close\r\n\r\n"

            all_data = protocol + Location + content + connection
            self.request.sendall(bytearray(all_data, "UTF-8"))

        elif status == "404":
            protocol = "HTTP/1.1 404 Not Found\r\n"
            content = "Content-type: application/octet-stream; charset=UTF-8\r\n"
            connection = "Connection: close\r\n\r\n"

            all_data = protocol + content + connection
            self.request.sendall(bytearray(all_data, "UTF-8"))

        elif status == "405":
            protocol = "HTTP/1.1 405 Method Not Allowed\r\n"
            content = "Content-type: application/octet-stream; charset=UTF-8\r\n"
            connection = "Connection: close\r\n\r\n"

            all_data = protocol + content + connection
            self.request.sendall(bytearray(all_data, "UTF-8"))

        elif status == "file":
            protocol, content, octet, connection, data = self.build(directory, status)
            all_data = protocol + content + octet + connection + data
            self.request.sendall(bytearray(all_data, "UTF-8"))

        elif status == "directory":
            # directory default is index.html
            directory = directory + html
            protocol, content, octet, connection, data = self.build(directory, status)
            all_data = protocol + content + octet + connection + data
            self.request.sendall(bytearray(all_data, "UTF-8"))            


    def build(self, directory, status):
        # getting the content type eg. html, css
        contype = directory.split("/")
        contype = contype[len(contype)-1]
        contype = contype.split(".")
        contype = contype[len(contype)-1]

        protocol = "HTTP/1.1 200 OK\r\n"
        content = "Content-type: text/" + contype + "; charset=UTF-8\r\n"
        f = os.path.abspath(directory)
        sz = os.path.getsize(f)
        sz = str(sz)
        octet = "content-length: " + sz + "\r\n"
        connection = "Connection: close\r\n\r\n"

        file = open(f, "r")
        data = file.read()
        #print("build compete")
        return protocol, content, octet, connection, data


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
