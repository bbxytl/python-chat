#!/usr/bin/env python
# encoding: utf-8
# __author__ = 'Long-T'

import socket
import threading
# import struct
import server_cmd
import protocol
import time
import os


class QQServer(object):
    def __init__(self, hostName, port, fileName):
        """
        users = { id : info }
        info = {'name':str, 'pwd':str, 'isOnline':Bool, \
                'socket':clientSocket, 'addr':clientAddr, 'friends':set([])}
        """
        self.__users = self.__initUsers(fileName)
        self.fileName = fileName
        self.__serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__serverSocket.bind((hostName, port))
        self.__serverSocket.listen(pt.LISTEN_MAX)
        print 'Waiting for connection ....'

    def __initUsers(self, fileName):
        users = {}
        if os.path.isfile(fileName) == False:
            return {}
        file = open(fileName)
        # read from file
        for line in file:
            info = {}
            friends = set([])
            print line.strip()
            userList = line.strip().split(' ')
            if len(userList) < 1:
                continue
            try:
                userId = int(userList[0])
                for infoNo in userList[1:]:
                    ls = infoNo.split(':')
                    key = int(ls[0])
                    val = ls[1]
                    if key != pt.USER_FRIENDS:
                        info[key] = val
                    else:
                        friends.add(val)
                info[pt.USER_ISONLINE] = not pt.FLAG_ONLINE
                info[pt.USER_SOCKET] = None
                info[pt.USER_ADDR] = None
                info[pt.USER_FRIENDS] = friends
                users[userId] = info
            except:
                file.close()
                return {}
        file.close()
        return users

    def saveUsers(self, fileName):
        data = []
        split = ':'
        space = ' '
        for id, info in self.getUsers().items():
            idtxt = str(id)
            friends = info[pt.USER_FRIENDS]
            fdtxt = ''
            for fd in friends:
                fdtxt = str(pt.USER_FRIENDS) + split + str(fd)
            nametxt = str(pt.USER_NAME) + split + info[pt.USER_NAME]
            pwdtxt = str(pt.USER_PWD) + split + info[pt.USER_PWD]
            line = (idtxt + space +
                    nametxt + space +
                    pwdtxt + space +
                    fdtxt + '\n')
            data.append(line)
        file = open(fileName, 'w')
        file.writelines(data)
        file.close()

    def getUsers(self):
        return self.__users

    def getUserName(self, userId):
        if userId in self.getUsers():
            return self.getUsers()[userId][pt.USER_NAME]

    def getUserId(self, userName):
        for id, info in self.getUsers().items():
            if info[pt.USER_NAME] == userName:
                return id

    def getUserPwd(self, userId):
        if userId in self.getUsers():
            return self.getUsers()[userId][pt.USER_PWD]

    def isUserOnline(self, userId):
        if userId in self.getUsers():
            return self.getUsers()[userId][pt.USER_ISONLINE]

    def getUserSocket(self, userId):
        if userId in self.getUsers():
            return self.getUsers()[userId][pt.USER_SOCKET]

    def getUserAddr(self, userId):
        if userId in self.getUsers():
            return self.getUsers()[userId][pt.USER_ADDR]

    def getFriends(self, userId):
        if userId in self.getUsers():
            return self.getUsers()[userId][pt.USER_FRIENDS]

    def getUsersOnline(self):
        onlines = {}
        for id, info in self.getUsers().items():
            if info[pt.USER_ISONLINE] == pt.FLAG_ONLINE:
                onlines[id] = info
        return onlines

    def setUserName(self, userId, newName):
        if userId in self.getUsers():
            oldName = self.__users[userId][pt.USER_NAME]
            self.__users[userId][pt.USER_NAME] = newName
            self.saveUsers(self.fileName)
            return oldName

    def modifyPwd(self, userId, oldPwd, newPwd):
        if userId in self.getUsers():
            if oldPwd == self.__users[userId][pt.USER_PWD]:
                self.__users[userId][pt.USER_PWD] = newPwd
                self.saveUsers(self.fileName)
                return oldPwd

    def setUserOnlineFlag(self, userId, flag):
        if userId in self.getUsers():
            oldFlag = self.__users[userId][pt.USER_ISONLINE]
            self.__users[userId][pt.USER_ISONLINE] = flag
            return oldFlag

    def setUserSocket(self, userId, newSocket):
        if userId in self.getUsers():
            oldSocket = self.__users[userId][pt.USER_SOCKET]
            self.__users[userId][pt.USER_SOCKET] = newSocket
            return oldSocket

    def setUserAddr(self, userId, newAddr):
        if userId in self.getUsers():
            oldAddr = self.__users[userId][pt.USER_ADDR]
            self.__users[userId][pt.USER_ADDR] = newAddr
            return oldAddr

    def addFriends(self, userId, addFrdId):
        if userId in self.getUsers():
            self.__users[userId][pt.USER_FRIENDS].add(addFrdId)
            self.saveUsers(self.fileName)
            return True
        else:
            return False

    def delFriends(self, userId, delFrdId):
        if userId in self.getUsers():
            self.__users[userId][pt.USER_FRIENDS].remove(delFrdId)
            self.saveUsers(self.fileName)
            return True
        else:
            return False

    def register(self, clientSocket, clientAddr, userId):
        text = 'You have to register first ! Are you Register ?(y/n):'  # Please input your : userId(integer must) userName userPwd :\n'
        pt.send(clientSocket, userId, pt.SERV_USER, pt.MSG_REGISTER, text)
        while True:
            toUser, fromUser, dataType, data = pt.recv(clientSocket)
            if data.strip() != '':
                break
        if dataType != pt.MSG_REGISTER:
            return None
        elif data != 'y' and data !='yes':
            return None
        else:
            text = 'Please input your : userId(must Integer) userName userPwd \n'
            print text
            pt.send(clientSocket, fromUser, pt.SERV_USER, pt.MSG_REGISTER, text)
            toUser, fromUser, dataType, data = pt.recv(clientSocket)
            dtlist = data.strip().split(' ')
            text = 'Input is Wrong !'
            if len(dtlist) != 3:
                pt.send(clientSocket, fromUser, pt.SERV_USER, pt.MSG_ERROR, text)
                return None
            else:
                userId = 0
                try:
                    userId = int(dtlist[0])
                    userName = dtlist[1]
                    userPwd = dtlist[2]
                except:
                    text = 'UserId is Wrong !'
                    pt.send(clientSocket, fromUser, pt.SERV_USER, pt.MSG_ERROR, text)
                    return None

                if userId in self.getUsers():
                    text = 'UserId exist !'
                    pt.send(clientSocket, fromUser, pt.SERV_USER, pt.MSG_ERROR, text)
                    return None
                if self.getUserId(userName)is not None:
                    text = 'UserName exist !'
                    pt.send(clientSocket, fromUser, pt.SERV_USER, pt.MSG_ERROR, text)
                    return None
                if self.registerUser(userId, userName, userPwd, clientSocket, clientAddr) == True:
                    text = '[from server] {0}:{1} Register OK ! PassWord : {2}'.format(userId, userName, userPwd)
                    pt.send(clientSocket, userId, pt.SERV_USER, pt.MSG_LOGON, text)
                    self.saveUsers(self.fileName)
                    return userId
                else:
                    text = 'Register  Wrong!'
                    pt.send(clientSocket, fromUser, pt.SERV_USER, pt.MSG_ERROR, text)

    def registerUser(self, userId, userName, userPwd, clientSocket, clientAddr):
        if userId in self.getUsers():
            return False
        try:
            info = {}
            info[pt.USER_NAME] = userName
            info[pt.USER_PWD] = userPwd
            info[pt.USER_ISONLINE] = pt.FLAG_ONLINE
            info[pt.USER_SOCKET] = clientSocket
            info[pt.USER_ADDR] = clientAddr
            friends = set([])
            info[pt.USER_FRIENDS] = friends

            self.__users[userId] = info
            print 'RegisterUser: [{0}:{1}] '.format(userId, userName)
            return True
        except:
            return False

    def logon(self, userId, userPwd, clientSocket, clientAddr):
        if userId not in self.getUsers():
            return None
        if userPwd != self.getUserPwd(userId):
            text = 'PassWord is Wrong !'
            pt.send(clientSocket, userId, pt.SERV_USER, pt.MSG_ERROR, text)
            return False
        else:
            self.setUserOnlineFlag(userId, pt.FLAG_ONLINE)
            self.setUserSocket(userId, clientSocket)
            self.setUserAddr(userId, clientAddr)
            return True

    def run(self):
        try:
            while True:
                clientSocket, clientAddr = self.__serverSocket.accept()
                thread = threading.Thread(target=self.clientLink, args=(clientSocket, clientAddr))
                thread.start()
        finally:
            self.saveUsers(self.fileName)

    def clientLink(self, clientSocket, clientAddr):
        print 'Accept new connection from %s:%s....' % clientAddr
        time.sleep(1)
        toUser, fromUser, dataType, data =pt.recv(clientSocket)
        userId = fromUser
        userPwd = data
        userSever = '0:server'
        if toUser != pt.SERV_USER or dataType != pt.MSG_LOGON or data is None or not data:
            text = 'Logon Error !'
            print text
        else:
            sg = self.logon(userId, userPwd, clientSocket, clientAddr)
            if sg is None:
                userId = self.register(clientSocket, clientAddr, userId)
                if userId is not None:
                    self.setUserOnlineFlag(userId, not pt.FLAG_ONLINE)
                return
            elif sg is False:
                return
            user = '{0}:{1}'.format(userId, self.getUserName(userId))  # %userId   self.getUserName(userId)
            sendText = '[{0}] Welcome {1}'.format(userSever, user)
            pt.send(clientSocket, userId, pt.SERV_USER, pt.MSG_LOGON, sendText)
            print sendText
            while True:
                toUser, fromUser, msgType, msg = pt.recv(clientSocket)
                fuser = '{0}:{1}'.format(fromUser, self.getUserName(fromUser))
                # no the toUser
                if toUser != pt.SERV_USER and toUser not in self.getUsers():
                    erroString = '[from {0} to {1} ] {2} not regist !'.format(userSever, fuser, toUser)
                    pt.send(clientSocket, fromUser, pt.SERV_USER, pt.MSG_TEXT, erroString)
                    print erroString
                # to the server ,should cmd
                elif toUser == pt.SERV_USER:
                    # print 'cmd ---->  toUser == {0}, fromUser == {1}, msgType == {2}, msg == {3} '.format(toUser,fromUser, msgType, msg)
                    sg = self.processCmd(fromUser, msg)
                    if sg == pt.MSG_QUIT:
                        break
                    elif sg == pt.MSG_ERROR:
                        erroString = '[from {0} to {1}] {2} : {3}'.format(userSever, fuser, msg, 'Wrong Cmd to Server !')
                        pt.send(clientSocket, fromUser, pt.SERV_USER, pt.MSG_ERROR, erroString)
                        print erroString
                # to other client
                else:
                    # print 'chat --->  toUser == {0}, fromUser == {1}, msgType == {2}, msg == {3} '.format(toUser,fromUser, msgType, msg)
                    sg = self.processChat(fromUser, toUser, msg)
                    if sg == pt.MSG_ERROR:
                        erroString = '[from {0} to {1}] {2} not online !'.format(userSever, fuser, toUser)
        clientSocket.close()

    def processCmd(self, userId, msg):
        clientSocket = self.getUserSocket(userId)
        if clientSocket is None:
            return pt.MSG_ERROR
        if not msg:
            return pt.MSG_ERROR
        res = pt.getcmd(msg)
        if res is None:
            return pt.MSG_ERROR
        cmdno = res[0]
        args = res[1]
        argss = [userId, clientSocket]

        text = pt.MAP_CMD_NO.keys()[pt.MAP_CMD_NO.values().index(cmdno)]
        for ag in args:
            argss.append(ag)
            text = text + "  " + ag
        print '{0}:{1} | {2}'.format(userId, self.getUserName(userId), text)

        return scmap.MAP_CMD_FUN[cmdno](self, argss)

    def processChat(self, fromUser, toUser, msg):
        # print toUser ,';' ,self.getUserName(toUser)
        toSocket = self.getUserSocket(toUser)
        if toSocket is None:
            return pt.MSG_ERROR
        text = '[{0}:{1}] {2}'.format(fromUser, self.getUserName(fromUser), msg)
        print text
        pt.send(toSocket, toUser, fromUser, pt.MSG_TEXT, text)

if __name__ == '__main__':
    import server_cmd_map
    pt = protocol
    sc = server_cmd
    scmap = server_cmd_map
    fileName = 'users.dat'
    qqServer = QQServer('127.0.0.1', 18889, fileName)
    qqServer.run()
