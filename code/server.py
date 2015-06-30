#!/usr/bin/env python
# encoding: utf-8
# __author__ = 'Long-T'

import socket
import threading
from threading import Thread
# import server_cmd as sc
import protocol as pt
import time
import os


class qqserver(object):
    def __init__(self, hostname, port, file_name):
        """
        users = { id : info }
        info = {'name':str, 'pwd':str, 'cmd':set([]), 'isOnline':Bool, \
                'socket':client_socket, 'addr':client_addr, 'friends':set([])}
        """
        self.__users = self.init_users(file_name)
        self.__file_name = file_name
        self.__done = False
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind((hostname, port))
        self.__server_socket.listen(pt.LISTEN_MAX)
        print 'Waiting for connection ....'

    def init_users(self, file_name):
        users = {}
        if os.path.isfile(file_name) == False:
            return {}
        file = open(file_name)
        # read from file
        for line in file:
            info = {}
            cmds = set([])
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
                    if key == pt.USER_CMD:
                        cmds.add(int(val))
                    elif key == pt.USER_FRIENDS:
                        friends.add(val)
                    else:
                        info[key] = val
                info[pt.USER_CMD] = cmds
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
            cmds = info[pt.USER_CMD]
            cdtxt = ''
            for cd in cmds:
                cdtxt = cdtxt + str(pt.USER_CMD) + split + str(cd) + space

            friends = info[pt.USER_FRIENDS]
            fdtxt = ''
            for fd in friends:
                fdtxt = fdtxt + str(pt.USER_FRIENDS) + split + str(fd) + space

            nametxt = str(pt.USER_NAME) + split + info[pt.USER_NAME]
            pwdtxt = str(pt.USER_PWD) + split + info[pt.USER_PWD]
            line = (idtxt + space +
                    nametxt + space +
                    pwdtxt + space +
                    cdtxt + space +
                    fdtxt + '\n')
            data.append(line)
        file = open(file_name, 'w')
        file.writelines(data)
        file.close()

    def get_server_socket(self):
        return self.__server_socket

    def get_file_name(self):
        return self.__file_name

    def set_file_name(self, file_name):
        self.__file_name = file_name

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

    def get_user_cmds(self, user_id):
        if user_id in self.get_users():
            return self.get_users()[user_id][pt.USER_CMD]

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
            self.save_users(self.__file_name)
            return oldname

    def modify_pwd(self, user_id, old_pwd, new_pwd):
        if user_id in self.get_users():
            if old_pwd == self.__users[user_id][pt.USER_PWD]:
                self.__users[user_id][pt.USER_PWD] = new_pwd
                self.save_users(self.__file_name)
                return old_pwd

    def issupportcmd(self, user_id, cmdno):
        if user_id in self.get_users():
            if cmdno in self.get_user_cmds(user_id):
                return True
            else:
                return False

    def add_cmd(self, user_id, cmdno):
        if user_id in self.get_users():
            if cmdno in pt.CMD_SET:
                self.__users[user_id][pt.USER_CMD].add(cmdno)
                return True
            else:
                return False

    def del_cmd(self, user_id, cmdno):
        if user_id in self.get_users():
            if cmdno in self.get_user_cmds(user_id):
                self.__users[user_id][pt.USER_CMD].remove(cmdno)
                return True
            else:
                return False

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
            self.save_users(self.__file_name)
            return True
        else:
            return False

    def del_friend(self, user_id, frd_id):
        if user_id in self.get_users():
            self.__users[user_id][pt.USER_FRIENDS].remove(frd_id)
            self.save_users(self.__file_name)
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
            pt.send(client_socket, user_id, pt.SERV_USER, pt.MSG_ERROR, "")
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
                    self.save_users(self.__file_name)
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
            info[pt.USER_CMD] = pt.USER_CMD_NORMAL
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

    class threadservercmd(Thread):

        def __init__(self, serv):
            Thread.__init__(self)
            self.setDaemon(True)
            self.serv = serv
            self.serv_socket = serv.__server_socket
            self.done = False

        def run(self):
            serv = self.serv
            while not self.done:
                data = raw_input()
                sg = serv.process_cmd(pt.SERV_USER, data)
                if sg == pt.MSG_QUIT:
                    serv.__done = True
                    self.done = True
                elif sg == pt.MSG_ERROR:
                    print "Error Cmd !"

    def run(self):
        try:
            thread_serv = threading.Thread(target=self.server_cmd)
            thread_serv.start()

            while True and not self.__done:
                    client_socket, client_addr = self.__server_socket.accept()
                    thread = threading.Thread(target=self.clientLink, args=(client_socket, client_addr))
                    thread.start()
        except KeyboardInterrupt:
            return
        finally:
            for uid, info in self.get_usersonline().items():
                client_socket = self.get_user_socket(uid)
                pt.send(client_socket, uid, pt.SERV_USER, pt.CMD_QUIT, "Server is Sign Out !")
            self.save_users(self.__file_name)

    def server_cmd(self):
        while not self.__done:
            try:
                data = raw_input()
                sg = self.process_serv_cmd(data)
                if sg == pt.MSG_QUIT:
                    self.__done = True
                elif sg == pt.MSG_ERROR:
                    print "Error Cmd !"
            except KeyboardInterrupt, e:
                print e
                return

    def process_serv_cmd(self, msg):
        if not msg:
            return pt.MSG_ERROR
        res = pt.getcmd(msg)
        if res is None:
            return pt.MSG_ERROR
        cmdno = res[0]
        args = res[1]
        argss = [pt.SERV_USER, self.get_server_socket()]
        try:
            if len(args) > 0:
                argss = [int(args[0]), self.get_server_socket()]
        except:
            return pt.MSG_ERROR
        text = pt.get_cmd_name(cmdno)
        # text = pt.MAP_CMD_NO.keys()[pt.MAP_CMD_NO.values().index(cmdno)]
        for ag in args[1:]:
            argss.append(ag)
            text = text + "  " + ag
        text = '[{0}:{1}] | {2}'.format(pt.SERV_USER, 'server', text)
        print text
        if cmdno not in pt.CMD_SET:
            text = text + "  | No this command !"
            print text
            return pt.MSG_ERROR
        return scmap.MAP_CMD_FUN[cmdno](self, argss)

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
                client_socket.close()
                print 'Close connection from %s:%s....' % client_addr
                return
            elif sg is False:
                client_socket.close()
                print 'Close connection from %s:%s....' % client_addr
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
        print 'Close connection from %s:%s....' % client_addr

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
        text = '{0}:{1} | {2}'.format(user_id,
                                      self.get_user_name(user_id),
                                      text)
        print text
        if self.issupportcmd(user_id, cmdno) is not True:
            text = text + "  | no authority or no this command !"
            pt.send(client_socket, user_id, pt.SERV_USER, pt.MSG_ERROR, text)
            return pt.MSG_ERROR
        return scmap.MAP_CMD_FUN[cmdno](self, argss)

    def process_chat(self, from_user, to_user, msg):
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
