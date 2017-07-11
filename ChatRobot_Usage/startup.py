import itchat
import log
import logging
import robot
from config import friend_wechat_remarknames

logger = logging.getLogger('MyItChatDemo')
reply_friends=[]


@itchat.msg_register(itchat.content.TEXT)
def msg_reply(msg):
    content = msg['Text']
    from_user_name = msg['FromUserName']
    from_user_remarkname = msg['User']['RemarkName']
    logger.info('receive {content} from remarkName:{FromUserRemarkName} userName:{username} '
        .format(content=content,FromUserRemarkName=from_user_remarkname,username=from_user_name))
    reply_content = robot.get_reply_msg(content, from_user_name)
    if from_user_name in reply_friends:
        logger.info('reply {content} to remarkName:{FromUserRemarkName} userName:{username} '
            .format(content=reply_content,FromUserRemarkName=from_user_remarkname,username=from_user_name))
        return reply_content


def get_username_with_remarknames(friend_wechat_remarknames):
    for remarkname in friend_wechat_remarknames:
        reply_friends.append(itchat.search_friends(remarkName=remarkname)[0]['UserName'])


def main():
    log.set_logging(loggingLevel=logging.INFO)
    itchat.auto_login(hotReload=True)
    user_info = itchat.search_friends()
    get_username_with_remarknames(friend_wechat_remarknames)
    logger.info('login success userInfo:{user_info}'.format(user_info=user_info))
    reply_friends.append(user_info['UserName'])
    itchat.run()

if __name__ == "__main__":
    main()
