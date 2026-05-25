"""
扬说财经 · 企业微信通知工具
用法: python notify-wecom.py "消息内容" [chatid]
默认发送到总指挥部群
"""
import json, subprocess, os, sys

CMD = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'npm', 'wecom-cli.cmd')
GROUP_CHAT = "wrrYiZLQAA1LwFFsrMlbPBPC--Gf1hIQ"
DM_CHAT = "wrrYiZLQAAHJywT9LI847dtlii1HSnNQ"

def send(message, chatid=None):
    if chatid is None:
        chatid = GROUP_CHAT
    msg = json.dumps({
        "chat_type": 2,
        "chatid": chatid,
        "msgtype": "text",
        "text": {"content": message}
    }, ensure_ascii=False)
    result = subprocess.run([CMD, "msg", "send_message", "--json", msg],
                            capture_output=True, text=True)
    return result.stdout

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "测试通知"
    cid = sys.argv[2] if len(sys.argv) > 2 else GROUP_CHAT
    print(send(msg, cid))
