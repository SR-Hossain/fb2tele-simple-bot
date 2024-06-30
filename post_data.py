from dataclasses import dataclass
from urllib.parse import unquote

@dataclass
class PostData:
    def __init__(self, url="", sender_name="Sender", text="", extra_links=[]):
        self.url = url
        self.sender_name = sender_name
        self.text = text
        self.extra_links = extra_links
        if "See translation" in self.text:
            self.text = self.text[: self.text.find("See translation")]
        self.text = self.text.replace(self.sender_name, "")
        first_greater_than_index = self.text.find(">")
        if first_greater_than_index != -1:
            self.text = (
                self.text[:first_greater_than_index]
                + self.text[first_greater_than_index + 1 :]
            )
        self.text = self.text.replace(self.sender_name, "")
        skip_from_group_name = self.text.find("SUST CSE (2019-20) Official")
        if skip_from_group_name != -1:
            self.text = self.text[
                skip_from_group_name + len("SUST CSE (2019-20) Official") :
            ]
        last_sust_cse_index = self.text.find("SUST CSE (2019-")
        if last_sust_cse_index != -1:
            self.text = self.text[:last_sust_cse_index]

        self.text = self.text.strip()

    def __repr__(self) -> str:
        return self.__dict__.__str__()


def get_post_data(post_url: str, send_request, environ) -> PostData:
    def get_extra_links():
        urls = []
        for post_url in post_content.findAll("a")[2:-2]:
            text = post_url.get_text()
            if text in ["See translation", "SUST CSE (2019-20) Official"]:
                continue
            post_url = post_url["href"]
            if "photo.php?" in post_url:
                try:
                    if post_url.startswith("/photo.php"):
                        post_url = f"https://mbasic.facebook.com{post_url}"
                    post_url = post_url.replace("amp;", "").replace("mbasic", "www")
                    post_url = (
                        send_request(post_url, headers=environ["WEB_FB_HEADER"])
                        .find(role="main")
                        .find("img")["src"]
                        .replace("amp;", "")
                    )

                    urls.append({"url": post_url, "text": "media url"})
                except:
                    print("Failed to fetch media url, url: ", post_url)
                    
            else:
                if post_url.startswith("/"):
                    if post_url.startswith("/hashtag"):
                        continue
                    elif post_url.startswith("/photo.php"):
                        text = "media url"
                        post_url = post_url.replace("amp;", "")
                    post_url = f"https://mbasic.facebook.com{post_url}"
                elif post_url.startswith("https://lm.facebook.com/l.php?u="):
                    post_url = unquote(
                        post_url[len("https://lm.facebook.com/l.php?u=") :]
                    )
                urls.append({"url": post_url, "text": text})
        return urls

    try:
        post_content = (
            send_request(post_url)
            .find(id="m_story_permalink_view")
            .find("div", class_="bl")
        )

        return PostData(
            url=post_url,
            sender_name=post_content.find("strong").get_text(),
            text=post_content.get_text(separator="\n"),
            extra_links=get_extra_links(),
        )

    except Exception as e:
        print("Failed to fetch post data, url: ", post_url)
        print("Error: ", e)

