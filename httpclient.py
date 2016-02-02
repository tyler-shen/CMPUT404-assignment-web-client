#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
from urlparse import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        # use sockets!
        con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if port == None:
            port = 80
        con.connect((host, port))  
        return con

    def get_code(self, data):
        if not data:
            return None
        code = int(data.split()[1])
        return code

    def get_headers(self,data):
        return None

    def get_body(self, data):
        if not data:
            return None
        body = data.split('\r\n\r\n')[1]
        return body

    # read everything from the socket
    def recvall(self, sock):
        sock.settimeout(2.0)
        buffer = bytearray()
        done = False
        while not done:
            try:
                part = sock.recv(1024)
            except:
                part = None
                done = True
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def findPath(self, url):
        part0 = url.split('://')[1]
        if '/' in part0:
            part1 = part0.split('/')[1:]
            if '?' in part1[len(part1)-1]:
                location = part1[len(part1)-1].find('?')
                last = part1[len(part1)-1][0:location]
                part1.pop()
                part1.append(last)
            part2 = '/'.join(part1)
            return '/'+part2
        else:
            return ''
        
    def findHost(self, url):
        part0 = url.split('://')[1]
        if '/' in part0:
            part1 = part0.split('/')[0]
            if ':' in part1:
                location = part1.find(':')
                part2 = part1[0:location]
                return part2
            else:
                return part1
        else:
            return part0
        
    def findPort(self, url):
        part0 = url.split('://')[1]
        if '/' in part0:
            part1 = part0.split('/')[0]
            if ':' in part1:
                location = part1.find(':') + 1
                part2 = part1[location:]
                return part2
            else:
                return None
        else:
            return None
    
    def GET(self, url, args=None):
        path = self.findPath(url)
        host = self.findHost(url)
        port = self.findPort(url)
        if port != None:
            port = int(port)
        
        request = 'GET ' + path + ' HTTP/1.1\r\n' + 'User-Agent: curl/7.29.0\r\n' + 'Host: ' + host + '\r\n' + 'Accept: */*\r\n\r\n'
        print request

        connection = self.connect(host, port)
        connection.sendall(request)
        response = self.recvall(connection)
        
        code = self.get_code(response)
        body = self.get_body(response)
        connection.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        path = self.findPath(url)
        host = self.findHost(url)
        port = self.findPort(url)
        if port != None:
            port = int(port)
        
        content = ''
        content_len = 0
        if args != None:
            content = urllib.urlencode(args)
            content_len = len(urllib.urlencode(args))
            
        request = 'POST ' + path + ' HTTP/1.1\r\n' + 'User-Agent: curl/7.29.0\r\n' + 'Host: ' + host + '\r\n' + 'Accept: */*\r\n' + 'Content-Length: ' + str(content_len) + '\r\n' + 'Content-Type: application/x-www-form-urlencoded\r\n\r\n' + content + '\r\n\r\n'
        print request
        
        connection = self.connect(host, port)
        connection.sendall(request)
        response = self.recvall(connection)
        
        code = self.get_code(response)
        body = self.get_body(response)
        connection.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[1], sys.argv[2] )
    else:
        print client.command( command, sys.argv[1] )   
