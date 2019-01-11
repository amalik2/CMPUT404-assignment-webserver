#  coding: utf-8
import os
import socketserver

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
    
    # Initializes member variables used throughout the process of handling a request
    def initResponseVars(self):
        self.statusCode = 200
        self.statusMessage = "OK"
        self.contentType = "text/plain"
        self.responseBody = ""

    # Handles an incoming HTTP request
    def handle(self):
        self.initResponseVars()
        self.data = self.request.recv(1024).strip().decode("utf8").split("\n")

        methodDetails = self.data[0].split(" ")
        # TODO: does the upper case conversion need to happen?
        method = methodDetails[0].upper()

        if (method == "GET"):
            self.handleGetRequest(methodDetails[1])
        else:
            self.statusCode = 405
            self.statusMessage = "Method Not Allowed"
            self.responseBody = "Only GET is supported."
        
        self.sendResponse()

    # Sets the status of the current request as one being made to a non-existant resource
    def setResourceNotFound(self):
        self.statusCode = 404
        self.statusMessage = "Resource Not Found"

    # Sets the status of the current request as one that has successfully reached a resource at the given path
    # @param {String} path - the path to the resource the request was made to
    def setResourceFound(self, path):
        try:
            resource = open(path)
            self.responseBody = resource.read()
            if (path.endswith(".html")):
                self.contentType = "text/html"
            elif (path.endswith(".css")):
                self.contentType = "text/css"
        except:
            self.statusCode = 500
            self.statusMessage = "Internal Server Error"

    # Handles the resource at the given path
    # @param {String} path - the absolute path to a resource
    def handleGetPath(self, path):
        if (os.path.isdir(path)):
            # Check for index.html existing in the specified directory
            indexPath = os.path.join(path, "index.html")
            if (os.path.exists(indexPath)):
                self.setResourceFound(indexPath)
            else:
                self.setResourceNotFound()
        else:
            self.setResourceFound(path)

    # Handles an incoming GET request
    # @param {String} path - the relative path to the resource to get, from the ./www/ directory
    def handleGetRequest(self, path):
        # From https://docs.python.org/3/library/os.path.html
        requestedPath = os.path.abspath("www" + path)
        if (os.path.join(os.getcwd(), "www") in requestedPath and os.path.exists(requestedPath)):
            self.handleGetPath(requestedPath)
        else:
            self.setResourceNotFound()

    # Builds a response to the current request being handled
    # @return {String} - the response to the request being handled
    def buildResponse(self):
        # Credit to https://stackoverflow.com/a/40828904 for example of Python string formatting
        # Credit to https://stackoverflow.com/a/28056437 and https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages#HTTP_Responses for what should be sent to the request
        response = "HTTP/1.1 %s %s\nConnection: close" % (self.statusCode, self.statusMessage)

        # Credit to https://stackoverflow.com/a/30686735 for string byte length
        response += "\nContent-Type: %s\nContent-Length: %d\n\n%s" % (self.contentType, len(self.responseBody.encode("utf-8")), self.responseBody)

        return response

    # Sends a response to the current request being serviced
    def sendResponse(self):
        self.request.sendall(bytearray(self.buildResponse(), "utf8"))
    
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
