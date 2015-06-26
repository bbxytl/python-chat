#!/usr/bin/env python
# encoding: utf-8
# __author__ = 'Long-T'

import socket
import threading
# import struct
import server_cmd as sc
import protocol as pt
import time
import os


class qqserver(object):
    def __init__(self, hostname, port, file_name):
        """
        users = { id : info }
        info = {'name':str, 'pwd':str, 'isOnline':Bool, \
                'socket':client_socket, 'addr':client_addr, 'friends':set([])}
        """
        self.__users = self.__init_users(file_name)
        self.file_name = file_name
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind((hostname, port))
        self.__server_socket.listen(pt.LISTEN_MAX)
        print 'Waiting for connection ....'

    def __init_users(self, file_name):
        users = {}
        if os.path.isfile(file_name) == False:
            return {}
        file = open(file_name)
        # read from file
        for line in file:
            info = {}
            friends = set([])
            print line.strip()
            userlist = line.strip().split(' ')
            if len(userlist) < 1:
                continue
            try:
                user_id = int(userlist[0])
                for infoNo in userlist[1:]:
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
                users[user_id] = info
            except:
                file.close()
                return {}
        file.close()
        return users

    def save_users(self, file_name):
        data = []
        split = ':'
        space = ' '
        for id, info in self.get_users().items():
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
        file = open(file_name, 'w')
        file.writelines(data)
        file.close()

    def get_users(self):
        return self.__users

    def get_user_name(self, user_id):
        if user_id in self.get_users():
            return self.get_users()[user_id][pt.USER_NAME]

    def get_user_id(self, user_name):
        for id, info in self.get_users().items():
            if info[pt.USER_NAME] == user_name:
                return id

    def get_user_pwd(self, user_id):
        if user_id in self.get_users():
            return self.get_users()[user_id][pt.USER_PWD]

    def isuseronline(self, user_id):
        if user_id in self.get_users():
            return self.get_users()[user_id][pt.USER_ISONLINE]

    def get_user_socket(self, user_id):
        if user_id in self.get_users():
            return self.get_users()[user_id][pt.USER_SOCKET]

    def get_user_addr(self, user_id):
        if user_id in self.get_users():
            return self.get_users()[user_id][pt.USER_ADDR]

    def get_user_friends(self, user_id):
        if user_id in self.get_users():
            return self.get_users()[user_id][pt.USER_FRIENDS]

    def get_usersonline(self):
        onlines = {}
        for id, info in self.get_users().items():
            if info[pt.USER_ISONLINE] == pt.FLAG_ONLINE:
                onlines[id] = info
        return onlines

    def set_user_name(self, user_id, new_name):
        if user_id in self.get_users():
            oldname = self.__users[user_id][pt.USER_NAME]
            self.__users[user_id][pt.USER_NAME] = new_name
            self.save_users(self.file_name)
            return oldname

    def modify_pwd(self, user_id, old_pwd, new_pwd):
        if user_id in self.get_users():
            if old_pwd == self.__users[user_id][pt.USER_PWD]:
                self.__users[user_id][pt.USER_PWD] = new_pwd
                self.save_users(self.file_name)
                return old_pwd

    def set_useronline_flag(self, user_id, flag):
        if user_id in self.get_users():
            old_flag = self.__users[user_id][pt.USER_ISONLINE]
            self.__users[user_id][pt.USER_ISONLINE] = flag
            return old_flag

    def set_user_socket(self, user_id, new_socket):
        if user_id in self.get_users():
            old_socket = self.__users[user_id][pt.USER_SOCKET]
            self.__users[user_id][pt.USER_SOCKET] = new_socket
            return old_socket

    def set_user_addr(self, user_id, new_addr):
        if user_id in self.get_users():
            old_addr = self.__users[user_id][pt.USER_ADDR]
            self.__users[user_id][pt.USER_ADDR] = new_addr
            return old_addr

    def add_friend(self, user_id, frd_id):
        if user_id in self.get_users():
            self.__users[user_id][pt.USER_FRIENDS].add(frd_id)
            self.save_users(self.file_name)
            return True
        else:
            return False

    def del_friend(self, user_id, frd_id):
        if user_id in self.get_users():
            self.__users[user_id][pt.USER_FRIENDS].remove(frd_id)
            self.save_users(self.file_name)
            return True
        else:
            return False

    def register(self, client_socket, client_addr, user_id):
        text = 'You have to register first ! Are you Register ?(y/n):'
        pt.send(client_socket, user_id, pt.SERV_USER, pt.MSG_REGISTER, text)
        while True:
            to_user, from_user, data_type, data = pt.recv(client_socket)
            if data.strip() != '':
                break
        if data_type != pt.MSG_REGISTER:
            return None
        elif data != 'y' and data != 'yes':
            return None
        else:
            text = 'Please input your : user_id(must Integer) user_name user_pwd \n'
            print text
            pt.send(client_socket, from_user, pt.SERV_USER, pt.MSG_REGISTER, text)
            to_user, from_user, data_type, data = pt.recv(client_socket)
            dtlist = data.strip().split(' ')
            text = 'Input is Wrong !'
            if len(dtlist) != 3:
                pt.send(client_socket, from_user, pt.SERV_USER, pt.MSG_ERROR, text)
                return None
            else:
                user_id = 0
                try:
                    user_id = int(dtlist[0])
                    user_name = dtlist[1]
                    user_pwd = dtlist[2]
                except:
                    text = 'UserId is Wrong !'
                    pt.send(client_socket, from_user, pt.SERV_USER, pt.MSG_ERROR, text)
                    return None

                if user_id in self.get_users():
                    text = 'UserId exist !'
                    pt.send(client_socket, from_user, pt.SERV_USER, pt.MSG_ERROR, text)
                    return None
                if self.get_user_id(user_name)is not None:
                    text = 'UserName exist !'
                    pt.send(client_socket, from_user, pt.SERV_USER, pt.MSG_ERROR, text)
                    return None
                if self.register_user(user_id, user_name, user_pwd, client_socket, client_addr) == True:
                    text = '[from server] {0}:{1} Register OK ! PassWord : {2}'.format(user_id,
                                                                                       user_name,
                                                                                       user_pwd)
                    pt.send(client_socket, user_id, pt.SERV_USER, pt.MSG_LOGON, text)
                    self.save_users(self.file_name)
                    return user_id
                else:
                    text = 'Register  Wrong!'
                    pt.send(client_socket, from_user, pt.SERV_USER, pt.MSG_ERROR, text)

    def register_user(self, user_id, user_name, user_pwd, client_socket, client_addr):
        if user_id in self.get_users():
            return False
        try:
            info = {}
            info[pt.USER_NAME] = user_name
            info[pt.USER_PWD] = user_pwd
            info[pt.USER_ISONLINE] = pt.FLAG_ONLINE
            info[pt.USER_SOCKET] = client_socket
            info[pt.USER_ADDR] = client_addr
            friends = set([])
            info[pt.USER_FRIENDS] = friends

            self.__users[user_id] = info
            print 'RegisterUser: [{0}:{1}] '.format(user_id, user_name)
            return True
        except:
            return False

    def logon(self, user_id, user_pwd, client_socket, client_addr):
        if user_id not in self.get_users():
            return None
        if user_pwd != self.get_user_pwd(user_id):
            text = 'PassWord is Wrong !'
            pt.send(client_socket, user_id, pt.SERV_USER, pt.MSG_ERROR, text)
            return False
        else:
            self.set_useronline_flag(user_id, pt.FLAG_ONLINE)
            self.set_user_socket(user_id, client_socket)
            self.set_user_addr(user_id, client_addr)
            return True

    def run(self):
        try:
            while True:
                client_socket, client_addr = self.__server_socket.accept()
                thread = threading.Thread(target=self.clientLink, args=(client_socket, client_addr))
                thread.start()
        finally:
            self.save_users(self.file_name)

    def clientLink(self, client_socket, client_addr):
        print 'Accept new connection from %s:%s....' % client_addr
        time.sleep(1)
        to_user, from_user, data_type, data = pt.recv(client_socket)
        user_id = from_user
        user_pwd = data
        user_sever = '0:server'
        if to_user != pt.SERV_USER or data_type != pt.MSG_LOGON or data is None or not data:
            text = 'Logon Error !'
            print text
        else:
            sg = self.logon(user_id, user_pwd, client_socket, client_addr)
            if sg is None:
                user_id = self.register(client_socket, client_addr, user_id)
                if user_id is not None:
                    self.set_useronline_flag(user_id, not pt.FLAG_ONLINE)
                return
            elif sg is False:
                return
            user = '{0}:{1}'.format(user_id, self.get_user_name(user_id))  # %user_id   self.get_user_name(user_id)
            send_text = '[{0}] Welcome {1}'.format(user_sever, user)
            pt.send(client_socket, user_id, pt.SERV_USER, pt.MSG_LOGON, send_text)
            print send_text
            while True:
                to_user, from_user, msg_type, msg = pt.recv(client_socket)
                fuser = '{0}:{1}'.format(from_user, self.get_user_name(from_user))
                # no the to_user
                if to_user != pt.SERV_USER and to_user not in self.get_users():
                    erro_string = '[from {0} to {1} ] {2} not regist !'.format(user_sever, fuser, to_user)
                    pt.send(client_socket, from_user, pt.SERV_USER, pt.MSG_TEXT, erro_string)
                    print erro_string
                # to the server ,should cmd
                elif to_user == pt.SERV_USER:
                    sg = self.process_cmd(from_user, msg)
                    if sg == pt.MSG_QUIT:
                        break
                    elif sg == pt.MSG_ERROR:
                        erro_string = '[from {0} to {1}] {2} : {3}'.format(user_sever,
                                                                           fuser,
                                                                           msg,
                                                                           'Wrong Cmd to Server !')
                        pt.send(client_socket, from_user, pt.SERV_USER, pt.MSG_ERROR, erro_string)
                        print erro_string
                # to other client
                else:
                    sg = self.process_chat(from_user, to_user, msg)
                    if sg == pt.MSG_ERROR:
                        erro_string = '[from {0} to {1}] {2} not online !'.format(user_sever,
                                                                                  fuser,
                                                                                  to_user)
        client_socket.close()

    def process_cmd(self, user_id, msg):
        client_socket = self.get_user_socket(user_id)
        if client_socket is None:
            return pt.MSG_ERROR
        if not msg:
            return pt.MSG_ERROR
        res = pt.getcmd(msg)
        if res is None:
            return pt.MSG_ERROR
        cmdno = res[0]
        args = res[1]
        argss = [user_id, client_socket]

        text = pt.MAP_CMD_NO.keys()[pt.MAP_CMD_NO.values().index(cmdno)]
        for ag in args:
            argss.append(ag)
            text = text + "  " + ag
        print '{0}:{1} | {2}'.format(user_id,
                                     self.get_user_name(user_id),
                                     text)

        return scmap.MAP_CMD_FUN[cmdno](self, argss)

    def process_chat(self, from_user, to_user, msg):
        # print to_user ,';' ,self.get_user_name(to_user)
        toSocket = self.get_user_socket(to_user)
        if toSocket is None:
            return pt.MSG_ERROR
        text = '[{0}:{1}] {2}'.format(from_user,
                                      self.get_user_name(from_user),
                                      msg)
        print text
        pt.send(toSocket, to_user, from_user, pt.MSG_TEXT, text)

if __name__ == '__main__':
    import server_cmd_map as scmap
    file_name = 'users.dat'
    qq_server = qqserver('127.0.0.1', 18889, file_name)
    qq_server.run()
