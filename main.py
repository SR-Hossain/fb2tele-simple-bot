import json
import requests
from bs4 import BeautifulSoup
from post_data import get_post_data
from flask import Flask
from tele_bot import TeleBot


app = Flask(__name__)

@app.route('/')
def hello_world():
    environ = eval(open(".env.json").read())

    def send_request(url, headers=environ["FACEBOOK_HEADERS"]):
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Error: ", response.status_code)
            return None
        return BeautifulSoup(response.content, "html.parser")

    post_links_in_groups = [
        int(a["href"][: a["href"].find("?refid")].split("/")[-2])
        for a in send_request(environ["GROUP_OR_PAGE_LINK"])
        .find(id="m_group_stories_container")
        .find_all("a", string="Full Story")
    ]

    new_post_permalink_ids = list(
        filter(lambda x: x > environ["LAST_POST_ID"], post_links_in_groups)
    )


    post_data = [
        get_post_data(f"{environ['GROUP_OR_PAGE_LINK']}/permalink/{post_id}", send_request=send_request, environ=environ)
        for post_id in new_post_permalink_ids
    ]

    telebot = TeleBot(
        environ["TELEGRAM_API_TOKEN"],
        environ["TELEGRAM_CHAT_ID"],
        environ["TELEGRAM_DEBUG_CHAT_ID"],
    )

    [telebot.send_message(p_data) for p_data in post_data[::-1]]
    environ['LAST_POST_ID'] = post_links_in_groups[0]

    with open(".env.json", "w") as f:
        f.write(json.dumps(environ, indent=4))
        
    return "Posted to telegram successfully..."