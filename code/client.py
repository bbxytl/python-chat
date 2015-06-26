#!/usr/bin/env python
# encoding: utf-8
# __author__ = 'Long-T'

import socket
import protocol
import sys
from threading import Thread

pt = protocol

class qqclient(object):
    def __init__(self, hostname, port):
        self.user_id = 1000
        self.user_name = 'n1000'
        self.curchatuser = pt.SERV_USER

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((hostname, port))
        print 'connect ....'

    def get_user_id(self):
        return self.user_id

    def get_user_name(self):
        return self.user_name

    def setCurChatUser(self, newChatUser):
        oldChatUser = self.curchatuser
        self.curchatuser = newChatUser
        return oldChatUser

    def set_user_id(self, newUserId):
        oldUserId = self.user_id
        self.user_id = newUserId
        return oldUserId

    def setUserName(self, newName):
        oldName = self.user_name
        self.user_name = newName
        return oldName

    def logon(self, user_id, user_pwd):
        pt.send(self.client_socket, pt.SERV_USER, user_id, pt.MSG_LOGON, user_pwd)
        toUser, fromUser, msgType, msg = pt.recv(self.client_socket)
        print msg
        if msgType == pt.MSG_LOGON:
            return True
        elif msgType == pt.MSG_ERROR:
            return False
        elif msgType == pt.MSG_REGISTER:

            while msgType == pt.MSG_REGISTER:
                msg = sys.stdin.readline().strip()
                pt.send(self.client_socket, pt.SERV_USER, user_id, pt.MSG_REGISTER, msg)
                toUser, fromUser, msgType, msg = pt.recv(self.client_socket)
                print msg
                if msgType == pt.MSG_LOGON:
                    return None
        return False

    def run(self, user_id, user_pwd):
        self.set_user_id(user_id)
        self.setCurChatUser(pt.SERV_USER)

        input = [self.client_socket, sys.stdin]

        try:
            if self.logon(user_id, user_pwd) != True:
                return
            self.commitwithserver(input)
        finally:
            self.client_socket.close()

    def commitwithserver(self, input):

        prostdin = processstdin(self)
        prostdin.start()

        sign = True
        while sign:
            toUser, fromUser, msgType, msg = pt.recv(self.client_socket)
            try:
                if msgType == pt.MSG_QUIT:
                    prostdin.done = True
                    return
                elif msgType == pt.MSG_CMD:
                    self.curchatuser = toUser
                elif msgType == pt.MSG_FRIEND_QUIT:
                    self.curchatuser = pt.SERV_USER
            finally:
                print msg


class processstdin(Thread):

    def __init__(self, client):
        Thread.__init__(self)
        self.setDaemon(True)
        self.client = client
        self.client_socket = client.client_socket
        self.done = False

    def run(self):
        client = self.client
        while not self.done:
            data = raw_input()
            dataType = pt.MSG_TEXT
            if len(data)>0 and data[0] == '/':
                dataType = pt.MSG_CMD
                client.curchatuser = pt.SERV_USER
            pt.send(self.client_socket, client.curchatuser, client.user_id, dataType, data)


if __name__ == '__main__':
    if len(sys.argv) !=3:
        print u'Wrong Argvs : user_id(integer), user_pwd '
    else:
        hostname = '127.0.0.1'
        port = 18889
        qq_client = qqclient(hostname, port)
        user_id = 0
        try:
            user_id =int(sys.argv[1])
            user_pwd = sys.argv[2]
            qq_client.run(user_id, user_pwd)
        except ValueError, e:
            pt.send(qq_client.client_socket, pt.SERV_USER, qq_client.user_id, pt.MSG_QUIT, '')
            print u'Wrong user_id(integer)!\nValueError: ', e
