import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message

load_dotenv()


machine = TocMachine(
    states=["user", "menu", "summation", "result", "my_profile", "show_fsm"],
    transitions=[
        {
            "trigger": "init",
            "source": "user",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "summation",
            "conditions": "is_going_to_summation",
        },
        {
            "trigger": "enter_number",
            "source": "summation",
            "dest": "result",
            "conditions": "is_going_to_result",
        },
        {
            "trigger": "go_back_to_summation",
            "source": "result",
            "dest": "summation",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "my_profile",
            "conditions": "is_going_to_my_profile",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "show_fsm",
            "conditions": "is_going_to_show_fsm",
        },
        {
            "trigger": "go_back",
            "source": ["summation", "my_profile", "show_fsm"],
            "dest": "menu"
        },
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue

        print(f"\nFSM STATE: {machine.state}")
        if(machine.state == "user"):
            response = machine.init(event)
        elif(machine.state == "menu"):
            response = machine.advance(event)
        elif(machine.state == "summation"):
            response = machine.enter_number(event)
            if(response == False):
                response = machine.go_back(event)

        print(f"REQUEST BODY: \n{body}")
        if response == False:
            send_text_message(event.reply_token, "Not Entering any State")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    PORT = int(os.environ['PORT'])
    app.run(host="0.0.0.0", port=PORT, debug=True, reloader=True)
