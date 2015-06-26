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
USER_ISONLINE = 2
USER_SOCKET = 3
USER_ADDR = 4
USER_FRIENDS = 5

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

MAP_CMD_NO = {'/name': CMD_NAME, '/n': CMD_NAME,
              '/online': CMD_ONLINE, '/o': CMD_ONLINE,
              '/rename': CMD_RENAME, '/r': CMD_RENAME,
              '/mdpwd': CMD_MDPWD, '/m': CMD_MDPWD,
              '/friends': CMD_FRIENDS, '/f': CMD_FRIENDS,
              '/addfriend': CMD_ADD_FRIEND, '/af': CMD_ADD_FRIEND,
              '/delfriend': CMD_DEL_FRIEND, '/df': CMD_DEL_FRIEND,
              '/chat': CMD_CHAT, '/c': CMD_CHAT,
              '/quit': CMD_QUIT, '/q': CMD_QUIT}


def pack(toUser, fromUser, endFlag, dataType, dataOrig):
        fomart = '>IIIII%ss' % len(dataOrig)
        streamString = struct.pack(fomart, toUser, fromUser, endFlag,
                                   dataType, len(dataOrig), dataOrig)
        return streamString


def unpack(streamString):
        fomart = '>IIIII'
        headLength = struct.calcsize(fomart)
        toUser, fromUser, endFlag, dataType, dataLength = struct.unpack(fomart, streamString[:headLength])
        data, = struct.unpack('>%ss' % dataLength,
                              streamString[headLength:headLength + dataLength])
        return toUser, fromUser, endFlag, dataType, dataLength, data


def recv(socket):
    msg = ''
    while True:
        streamData = socket.recv(PROTOCOL_MAX_SIZE)
#       print str(streamData)
        toUser, fromUser, endFlag, dataType, dataLength, data = unpack(streamData)
        msg = msg + data
        if endFlag == FLAG_ENDOFDATA:
            return toUser, fromUser, dataType, msg
        elif len(msg) >= ONE_DATA_MAX_SIZE:
            return None, None, None, None


def send(socket, toUser, fromUser, dataType, data):
    sg = True
    end = not FLAG_ENDOFDATA
    while sg:
        if len(data) < DATA_MAX_LEN:
            end = FLAG_ENDOFDATA
        dt = data[:DATA_MAX_LEN]
        stream = pack(toUser, fromUser, end, dataType, dt)
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
