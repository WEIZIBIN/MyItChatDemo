import logging
import itchat
import robot
import log
from config import friend_wechat_remarknames,reply_msg_from_myself

logger = logging.getLogger('MyItChatDemo')
reply_friends = []


@itchat.msg_register(itchat.content.TEXT)
def msg_reply(msg):
    print(msg)
    content = msg['Text']
    from_user_name = msg['FromUserName']
    from_user_remarkname = msg['User']['RemarkName']
    logger.info('receive text : {content} from remarkName:{FromUserRemarkName} to userName:{username} '
        .format(content=content,FromUserRemarkName=from_user_remarkname,username=from_user_name))
    try:
        reply_content = robot.get_reply_msg(content, from_user_name)
    except Exception as e:
        logger.error('get reply from robot failed: %s' % e)
        return
    if is_auto_replay(from_user_name) :
        logger.info('reply {content} to remarkName:{FromUserRemarkName} userName:{username} '
            .format(content=reply_content,FromUserRemarkName=from_user_remarkname,username=from_user_name))
        return reply_content


@itchat.msg_register(itchat.content.PICTURE)
def msg_reply(msg):
    from_user_name = msg['FromUserName']
    from_user_remarkname = msg['User']['RemarkName']
    logger.info('receive unsupported content from remarkName:{FromUserRemarkName} from userName:{username} '
                .format(FromUserRemarkName=from_user_remarkname, username=from_user_name))
    if is_auto_replay(from_user_name):
        return '好好聊天，不要发表情、语音……'


def is_auto_replay(from_user_name):
    return from_user_name in reply_friends


def get_username_with_remarknames(friend_wechat_remarknames):
    for remarkname in friend_wechat_remarknames:
        friends = itchat.search_friends(remarkName=remarkname)
        for friend in friends:
            reply_friends.append(friend['UserName'])


def main():
    log.set_logging(loggingLevel=logging.INFO)
    itchat.auto_login(hotReload=True)
    user_info = itchat.search_friends()
    get_username_with_remarknames(friend_wechat_remarknames)
    logger.info('login success userInfo:{user_info}'.format(user_info=user_info))
    if reply_msg_from_myself:
        reply_friends.append(user_info['UserName'])
    itchat.run()

if __name__ == "__main__":
    main()
