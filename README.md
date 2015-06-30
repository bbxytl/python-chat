# python-chat
使用python编写的简单聊天程序，主要是练习协议的制定以及网络编程等

## 运行
- 首先运行服务器：

```python
python server.py
```

- 然后是客户端，参数为两个 [userId] [userPassWord]

```python
python client.py 11 123456
```

- 首次运行密码可以随意输入，然后进入交互注册环节。
- 客户端可向服务器发送指令以让服务器运行；
- 客户端与客户端之间进行文本聊天。

## 支持的命令参照：
新用户默认拥有的命令使用 `*` 号标识！
- `/names`  :  `*` 显示所有注册的用户id和用户名
- `/online`	:  `*` 显示目前在线的用户id和用户名
- `/rename [newUserName]` :  `*` 客户端改名（用户名）
- `/mdpwd [oldPassWord] [newPassWord]` 	:  `*` 修改密码
- `/quit`   :  `*` 客户端退出
- `/chat [UserId]` :  `*` 和指定用户聊天
- `/friends` :  `*` 当前用户的好友列表
- `/addfriend [userId]`:  `*` 添加好友
- `/delfriend [userId]`:  `*` 删除好友
- `/updateuser [fileName]`	: 更新用户数据文件,fileName 为可选项，如果有，则表示将目前的用户数据先存档到 fileName ,在从原来的数据文件载入数据，主要用于直接手动更改 users.dat 后加载，否则手动更改会无效。
- `/getcmds` ：  `*` 获取当前用户所支持的所有命令列表 `全命令名 | 命令别名 ： 命令编号`，服务器拥有全部命令
- `/addcmd [userId] [newCmdNo]` ： 给用户添加命令，使用命令编号
- `/delcmd [userId] [cmdNo]` : 取消某用户的命令权限，使用命令编号 
- 命令的别名：
	- `/names` --> `/n`	
	- `/online` --> `/o`
	- `/rename` --> 	`/r`
	- `/mdpwd` --> `/m`
	- `/quit` --> `/q`
	- `/chat` --> `/c`
	- `/friends` --> `/f`
	- `/addfriend` --> `/af`
	- `/delfriend` --> `/df`
	- `/getcmds` --> `/upuser`
	- `/addcmd` --> `/ac`
	- `/delcmd`  --> `/dc`


---