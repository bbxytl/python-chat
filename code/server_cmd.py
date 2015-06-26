#!/usr/bin/env python
# encoding: utf-8
# coding style: pep8
# __author__ = 'Long-T'

import protocol as pt


def cmd_name(serv, args):
    # print " cmd _ name()"
    user_id = args[0]
    client_socket = args[1]

    names = serv.get_users()
    text = ''
    for id, info in names.items():
        text = text + str(id) + ':' + serv.get_user_name(id) + '\n'
    pt.send(client_socket, user_id, pt.SERV_USER, pt.MSG_TEXT, text)


def cmd_online(serv, args):
    # print " cmd_online"
    user_id = args[0]
    client_socket = args[1]

    users = serv.get_usersonline()
    names = ''
    for uid in users.keys():
        names = names + str(uid) + ':' + serv.get_user_name(uid) + '\n'
    pt.send(client_socket, user_id, pt.SERV_USER, pt.MSG_TEXT, names)


def cmd_rename(serv, args):
    # print "cmd_rename()"
    if len(args) < 2:
        return pt.MSG_ERROR
    user_id = args[0]
    client_socket = args[1]
    if len(args) > 2:
        msg = args[2]
    old_name = serv.set_user_name(user_id, msg)
    if old_name is None:
        return pt.MSG_ERROR
    else:
        for uid, info in serv.get_usersonline().items():
            client_socket = serv.get_user_socket(uid)
            msg = '[{0}] now call :[{1}]'.format(old_name, msg)
            pt.send(client_socket, uid, pt.SERV_USER, pt.MSG_TEXT, msg)


def cmd_mdpwd(serv, args):
    # print " cmd_mdpwd"
    user_id = args[0]
    client_socket = args[1]

    if len(args) < 4:
        return pt.MSG_ERROR
    input_oldpwd = args[2]
    input_newpwd = args[3]
    old_pwd = serv.get_user_pwd(user_id)
    if serv.modify_pwd(user_id, input_oldpwd, input_newpwd) == True:
        text = '[{0}:{1}] old PassWord is : {2}, Now is {3}'.format(user_id,
                                                                    serv.get_user_name(user_id),
                                                                    old_pwd,
                                                                    input_newpwd)
        pt.send(client_socket, user_id, pt.SERV_USER, pt.MSG_TEXT, text)
    else:
        return pt.MSG_ERROR


def cmd_friends(serv, args):
    # print "cmd_friends"
    user_id = args[0]
    client_socket = args[1]

    friends = serv.get_user_friends(user_id)
    text = ''
    for uid in friends:
        ol = '  '
        uid = int(uid)
        if serv.isuseronline(uid) == pt.FLAG_ONLINE:
            ol = '* '
        text = text + ol + str(uid) + ':' + serv.get_user_name(uid) + '\n'
    pt.send(client_socket, user_id, pt.SERV_USER, pt.MSG_TEXT, text)


def cmd_add_friend(serv, args):
    # print "cmd_add_friend"
    user_id = args[0]
    client_socket = args[1]

    if len(args) < 3:
        return pt.MSG_ERROR
    try:
        fdId = int(args[2].strip())
        if fdId not in serv.get_users():
            text = '%s is not regist !' % fdId
            pt.send(client_socket, user_id, pt.SERV_USER, pt.MSG_ERROR, text)
        if serv.add_friend(user_id, fdId):
            text = 'You have a new friend :[{0}:{1}]'.format(fdId, serv.get_user_name(fdId))
            pt.send(client_socket, user_id, pt.SERV_USER, pt.MSG_TEXT, text)
    except:
        return pt.MSG_ERROR


def cmd_del_friend(serv, args):
    # print "cmd_del_friend"
    user_id = args[0]
    client_socket = args[1]

    if len(args) < 3:
        return pt.MSG_ERROR
    try:
        fdId = int(args[2].strip())
        if fdId not in serv.get_user_friends(user_id):
            text = '[{0}:{1}] is not your friend ! Can\'t delete !'.format(fdId, serv.get_user_name(fdId))
            pt.send(client_socket, user_id, pt.SERV_USER, pt.MSG_ERROR, text)
        else:
            text = '[{0}:{1}] delete from your friends !'.format(fdId, serv.get_user_name(fdId))
            text = text + ' Now he/she is not your friend !'
            pt.send(client_socket, user_id, pt.SERV_USER, pt.MSG_TEXT, text)
    except:
        return pt.MSG_ERROR


def cmd_chat(serv, args):
    # print "cmd_chat"
    user_id = args[0]
    client_socket = args[1]

    if len(args) < 3:
        return pt.MSG_ERROR
    chatWithUserId = 0
    try:
        chatWithUserId = int(args[2].strip())
    except:
        return pt.MSG_ERROR
    fdName = serv.get_user_name(chatWithUserId)
    text = ''
    if chatWithUserId not in serv.get_users().keys():
        text = '%s is not regist !' % chatWithUserId
        chatWithUserId = pt.SERV_USER
    elif chatWithUserId not in serv.get_usersonline():
        text = '%s is not online !' % fdName
        chatWithUserId = pt.SERV_USER
    elif chatWithUserId not in serv.get_user_friends(user_id):
        text = '[{0}:{1}] is not your friend ! Please add he/she first !'.format(chatWithUserId, fdName)
        chatWithUserId = pt.SERV_USER
    else:
        text = 'You are chating with:  [{0}:{1}]'.format(chatWithUserId, fdName)
    pt.send(client_socket, chatWithUserId, pt.SERV_USER, pt.MSG_CMD, text)


def cmd_quit(serv, args):
    # print "cmd_quit"
    user_id = args[0]
    client_socket = args[1]
    serv.set_useronline_flag(user_id, not pt.FLAG_ONLINE)

    user_sever = '0:server'
    fuser = '{0}:{1}'.format(user_id, serv.get_user_name(user_id))
    quitString = '[from {0} to {1}] {1} Quit !'.format(user_sever, fuser)
    for id in serv.get_usersonline().keys():
        if id != user_id:
            onLineSocket = serv.get_user_socket(id)
            pt.send(onLineSocket, id, pt.SERV_USER, pt.MSG_FRIEND_QUIT, quitString)
    pt.send(client_socket, user_id, pt.SERV_USER, pt.MSG_QUIT, quitString)
    print quitString
    return pt.MSG_QUIT
