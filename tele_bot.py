from dataclasses import dataclass
from time import sleep
import requests
from post_data import PostData


@dataclass
class TeleBot:
    def __init__(self, api_token, channel_id, debug_channel_id):
        self.api_token = api_token
        self.channel_id = channel_id
        self.debug_channel_id = debug_channel_id

    def send_message(self, post_data: PostData, debug=False):
        message = f'<i><b><a href="{post_data.url}">{post_data.sender_name}</a></b></i>'
        if any(
            substring in post_data.text
            for substring in [
                "Class Routine",
                "A Section:",
                "B Section:",
                "Both Section:",
            ]
        ):
            message += (
                f'<pre><code class="language-Routine">{post_data.text}</code></pre>'
            )
        else:
            message += f"<pre>Post</pre><b>{post_data.text}</b>"

        image_links = [
            link["url"] for link in post_data.extra_links if link["text"] == "media url"
        ]
        normal_links = [
            link for link in post_data.extra_links if link["text"] != "media url"
        ]
        if normal_links:
            message += f"<pre>Extra Links</pre>"
            for link in normal_links:
                message += f'<a href="{link["url"]}">{link["text"]}</a>'

        try:
            response = None
            if post_data.text:
                response = requests.post(
                    url=f"https://api.telegram.org/bot{self.api_token}/sendMessage",
                    data={
                        "chat_id": (
                            self.channel_id if not debug else self.debug_channel_id
                        ),
                        "text": message,
                        "parse_mode": "html",
                        "disable_web_page_preview": True,
                    },
                )
                # print(f"response content: {response.content}")
        except:
            self.send_error_message("Failed to send message.")
            return 403
        if image_links:
            self.send_media_message(image_links, debug=debug)
        sleep(2)

    def send_error_message(self, e):
        error_message = f'@ssh_rezvi<pre><code class="language-FIXME">{e}</code></pre>'

        requests.post(
            url=f"https://api.telegram.org/bot{self.api_token}/sendMessage",
            data={
                "chat_id": self.debug_channel_id,
                "text": error_message,
                "parse_mode": "html",
                "disable_web_page_preview": True,
            },
        )

        # print("error message sent")
        sleep(2)

    def send_media_message(self, image_links, debug=False):
        some_error = False
        for media_url in image_links:
            # print(f'sending image {media_url}....')
            response = requests.post(
                url=f"https://api.telegram.org/bot{self.api_token}/sendPhoto",
                data={
                    "chat_id": self.channel_id if not debug else self.debug_channel_id,
                    "photo": media_url,
                    "parse_mode": "html",
                },
            )
            # print(f"media response: {response.content}")
            # print(f"media response status code: {response.status_code}")
            sleep(2)
            
            if response.status_code != 200:
                # print("Failed to send media message.", str(response.json))
                self.send_error_message("Failed to send media message, ", media_url)
        return 200 if not some_error else 403