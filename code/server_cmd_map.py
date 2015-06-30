#!/usr/bin/env python
# encoding: utf-8
# coding style: pep8
# __author__ = 'Long-T'

import protocol as pt
import server_cmd as sc


MAP_CMD_FUN = {pt.CMD_NAME: sc.cmd_name,
               pt.CMD_ONLINE: sc.cmd_online,
               pt.CMD_RENAME: sc.cmd_rename,
               pt.CMD_MDPWD: sc.cmd_mdpwd,
               pt.CMD_FRIENDS: sc.cmd_friends,
               pt.CMD_ADD_FRIEND: sc.cmd_add_friend,
               pt.CMD_DEL_FRIEND: sc.cmd_del_friend,
               pt.CMD_CHAT: sc.cmd_chat,
               pt.CMD_UPDATE_USERS: sc.cmd_update_users,
               pt.CMD_GET_CMDS: sc.cmd_get_cmds,
               pt.CMD_ADD_CMD: sc.cmd_add_cmd,
               pt.CMD_DEL_CMD: sc.cmd_del_cmd,
               pt.CMD_QUIT: sc.cmd_quit}
