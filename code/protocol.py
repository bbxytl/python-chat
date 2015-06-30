#!/usr/bin/env python
# encoding: utf-8
# __author__ = 'Long-T'

import struct

LISTEN_MAX = 5

TOUSER_LEN = 4
FROMUSER_LEN = 4
END_FLAG_LEN = 4
DATA_TYPE_LEN = 4
DATALENGTH_LEN = 4
DATA_MAX_LEN = 1024

PROTOCOL_MAX_SIZE = (TOUSER_LEN + FROMUSER_LEN + END_FLAG_LEN +
                     DATA_TYPE_LEN + DATALENGTH_LEN + DATA_MAX_LEN)
if PROTOCOL_MAX_SIZE % 4 != 0:
    PROTOCOL_MAX_SIZE = PROTOCOL_MAX_SIZE + 4 - PROTOCOL_MAX_SIZE % 4

ONE_DATA_MAX_SIZE = 1024 * 10

SERV_USER = 0
SERV_PORT = 18888
SERV_HOST = '127.0.0.1'

MSG_REGISTER = 0
MSG_LOGON = 1
MSG_QUIT = 4
MSG_CMD = 2
MSG_TEXT = 3
MSG_ERROR = 5
MSG_FRIEND_QUIT = 6

FLAG_ENDOFDATA = 0
FLAG_ONLINE = True

# 用户信息
USER_NAME = 0
USER_PWD = 1
USER_CMD = 2
USER_ISONLINE = 3
USER_SOCKET = 4
USER_ADDR = 5
USER_FRIENDS = 6

# 命令映射
CMD_NAME = 0
CMD_ONLINE = 1
CMD_RENAME = 2
CMD_MDPWD = 3
CMD_FRIENDS = 4
CMD_ADD_FRIEND = 5
CMD_DEL_FRIEND = 6
CMD_CHAT = 7
CMD_QUIT = 8
CMD_UPDATE_USERS = 9
CMD_GET_CMDS = 10
CMD_ADD_CMD = 11
CMD_DEL_CMD = 12

# 命令集合
CMD_SET = set([CMD_NAME,
               CMD_ONLINE,
               CMD_RENAME,
               CMD_MDPWD,
               CMD_FRIENDS,
               CMD_ADD_FRIEND,
               CMD_DEL_FRIEND,
               CMD_CHAT,
               CMD_UPDATE_USERS,
               CMD_GET_CMDS,
               CMD_ADD_CMD,
               CMD_DEL_CMD,
               CMD_QUIT])

# 默认用户拥有的命令集合
USER_CMD_NORMAL = set([CMD_NAME,
                       CMD_ONLINE,
                       CMD_RENAME,
                       CMD_MDPWD,
                       CMD_FRIENDS,
                       CMD_ADD_FRIEND,
                       CMD_DEL_FRIEND,
                       CMD_CHAT,
                       CMD_GET_CMDS,
                       CMD_QUIT])

# 命令的显式输入字符串
MAP_CMD_NO = {'/name': CMD_NAME, '/n': CMD_NAME,
              '/online': CMD_ONLINE, '/o': CMD_ONLINE,
              '/rename': CMD_RENAME, '/r': CMD_RENAME,
              '/mdpwd': CMD_MDPWD, '/m': CMD_MDPWD,
              '/friends': CMD_FRIENDS, '/f': CMD_FRIENDS,
              '/addfriend': CMD_ADD_FRIEND, '/af': CMD_ADD_FRIEND,
              '/delfriend': CMD_DEL_FRIEND, '/df': CMD_DEL_FRIEND,
              '/chat': CMD_CHAT, '/c': CMD_CHAT,
              '/updateuser': CMD_UPDATE_USERS, '/upuser': CMD_UPDATE_USERS,
              '/getcmds': CMD_GET_CMDS, '/gc': CMD_GET_CMDS,
              '/addcmd': CMD_ADD_CMD, '/ac': CMD_ADD_CMD,
              '/delcmd': CMD_DEL_CMD, '/dc': CMD_DEL_CMD,
              '/quit': CMD_QUIT, '/q': CMD_QUIT}


def get_cmd_name(cmdno):
    lst = []
    for key, no in MAP_CMD_NO.items():
        if no == cmdno:
            lst.append(key)
    text = '|'.join(lst)
    return text


def pack(to_user, from_user, end_flag, data_type, data_orig):
        fomart = '>IIIII%ss' % len(data_orig)
        stream_string = struct.pack(fomart, to_user, from_user, end_flag,
                                    data_type, len(data_orig), data_orig)
        return stream_string


def unpack(stream_string):
        fomart = '>IIIII'
        head_length = struct.calcsize(fomart)
        to_user, from_user, end_flag, data_type, data_length = struct.unpack(fomart, stream_string[:head_length])
        data, = struct.unpack('>%ss' % data_length,
                              stream_string[head_length:head_length + data_length])
        return to_user, from_user, end_flag, data_type, data_length, data


def recv(socket):
    msg = ''
    while True:
        stream_data = socket.recv(PROTOCOL_MAX_SIZE)
#       print str(stream_data)
        to_user, from_user, end_flag, data_type, data_length, data = unpack(stream_data)
        msg = msg + data
        if end_flag == FLAG_ENDOFDATA:
            return to_user, from_user, data_type, msg
        elif len(msg) >= ONE_DATA_MAX_SIZE:
            return None, None, None, None


def send(socket, to_user, from_user, data_type, data):
    sg = True
    end = not FLAG_ENDOFDATA
    while sg:
        if len(data) < DATA_MAX_LEN:
            end = FLAG_ENDOFDATA
        dt = data[:DATA_MAX_LEN]
        stream = pack(to_user, from_user, end, data_type, dt)
        socket.send(stream)
        if len(data) >= DATA_MAX_LEN:
            data = data[DATA_MAX_LEN:]
        else:
            data = ''
        if len(data) <= 0:
            break


def getcmd(msg):
    """ 根据输入判断是否是 命令，如果是，则获取命令的编号和命令的参数
        return：
            cmd -- 命令编号
            args -- 命令参数，是一个 元组

        input:
            msg -- 要判别的信息
    """
    dt = msg.strip().split(' ')
    ct = dt.count('')
    while ct > 0:
        dt.remove('')
        ct = ct - 1
    if len(dt) < 1 or dt[0][0] != '/':
        return None
    if dt[0] not in MAP_CMD_NO.keys():
        return None
    cmd = MAP_CMD_NO[dt[0]]
    args = dt[1:]
    return (cmd, args)
