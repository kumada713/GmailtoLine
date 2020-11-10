import os

from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import TextSendMessage

load_dotenv()

channel_access_token = os.environ.get("CHANNEL_ACCESS_TOKEN")
line_user_id = os.environ.get("LINE_USER_ID")
line_bot_api = LineBotApi(channel_access_token)


def push_message(content):
    line_bot_api.push_message(line_user_id, TextSendMessage(text=content))
