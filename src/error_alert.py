import notifiers
from notifiers import get_notifier
import now_bst
import os
import re

# notify when: python scripts have error/exceptions + channels that are offline

now = now_bst.now()
token = os.environ.get('mcc_error_notify_bot_token')
chat_id = os.environ.get('mcc_error_notify_grp_chat_id')

pushover = notifiers.get_notifier('pushover')

telegram = get_notifier('telegram')


index_list = [[33, 45], [46, 47], [58, 64], [91, 96], [123, 126]]
special = []
for i in index_list:
    for j in range(i[0], i[1]):
        special.append(chr(j))


def escape(string):
    replace = ['\\' + l for l in special]
    trans = str.maketrans(dict(zip(special, replace)))
    res = string.translate(trans)
    return res


def tele_notify(msg='', remarks=''):
     return telegram.notify(message=now + ' ' + remarks + escape(msg),
                        token=token,
                        chat_id=chat_id,
                        parse_mode='markdown')


def main():
    return tele_notify(remarks='*TASK SCHEDULER FAILED*')

if __name__ == "__main__":
    main()
