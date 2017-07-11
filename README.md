
MyItChat - A ItChat Usage Demo
===
[![MyItChatDeomo](https://img.shields.io/badge/MyItChatDemo-v1.0.0-brightgreen.svg)]()
[![ItChat](https://img.shields.io/badge/ItChat-v1.3.8-brightgreen.svg)](https://github.com/littlecodersh/ItChat)
[![Python](https://img.shields.io/badge/Python-v3.6-brightgreen.svg)](https://www.python.org/)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg)]()

这是一个ItChat个人使用例子，这里使用ItChat作为微信客户端组件，可以开发出许多有趣且实用的功能，接下面会详细说明。

欢迎star、fork、use、Issue：


依赖
---

* Python3
* ItChat(v1.3.8)


快速开始
---

* 使用命令安装ItChat
```python
pip install itchat
```
* 运行startup.py


自定义
---

* ./config.py

    * 替换自己的图灵机器人
    ```python
    tuling_apiUrl = 'tuling_api'
    tuling_key = 'your_tuling_key'
    ```
    * 自定义回复的微信昵称（只回复昵称为数组中的消息）
    ```python
    friend_wechat_remarknames = ['孙俪','邓超','范冰冰']
    ```
    * 自定义是否回复自己账号的消息（方便测试）
    ```python
    reply_msg_from_myself = True
    ```
    

已实现功能
---

* 接入图灵机器人
* 智能识别微信昵称回复


待实现功能
---

* 接入微软小冰机器人
* 智能监测好友是否删除自己

	持续更新开启更多功能


版本更新
---

* v1.0.0
    * 第一次提交
    * 接入图灵机器人
    * 智能识别微信昵称回复
