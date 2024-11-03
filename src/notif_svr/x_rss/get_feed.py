"""XBot"""
import datetime
import json
import logging
import os
import pickle
import re
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import reduce
from pathlib import Path
from typing import Any
from typing import Callable

import geckodriver_autoinstaller  # import Geckodriver into your program
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

geckodriver_autoinstaller.install()

port = 465  # For SSL
password = "bhyd tmjq tgdf ebsc"
sender_email = "noreply@myleft.org"

os.environ.update(ENV="production")
os.environ.update(AUTH_COOKIE=os.getcwd() + "/auth_cookie")
os.environ.update(VISITED_HASH_PATH=os.getcwd() + "/_visited.json")
os.environ.update(
    PRODUCT_IMG_PATH=os.getcwd()
    + "/src/notif_svr/media/myleft_ad.png"
)
os.environ.update(
    CLICK_BAIT_PATH=os.getcwd()
    + "/src/notif_svr/media/candDLetter.png"
)
os.environ.update(UNAME="myleftsnuts")
os.environ.update(P_WORD="Lmfuzzinao$1")
os.environ.update(TIMEOUT="10")


ENV = os.environ.get("ENV", "")
AUTH_COOKIE = os.environ.get("AUTH_COOKIE", "")
UNAME = os.environ.get("UNAME", "")
PWORD = os.environ.get("P_WORD", "")
VISITED_HASH_PATH = os.environ.get("VISITED_HASH_PATH", "")
PRODUCT_IMG_PATH = os.environ.get("PRODUCT_IMG_PATH", "")
CLICK_BAIT_PATH = os.environ.get("CLICK_BAIT_PATH", "")
TIMEOUT = int(os.environ.get("TIMEOUT", "10"))
HOME = "https://www.x.com/home"


def time_to_string(_time: float | int) -> str:
    """Convert Unix Timestamp to string."""
    datetime_object = datetime.datetime.fromtimestamp(_time)

    # Format the datetime object into a string
    return datetime_object.strftime("%Y-%m-%d %H:%M:%S")


def send_report(success: list[tuple[str, str]]) -> None:
    """Send order confirmation email

    Args:
        order (dict[str, Any]): order
        line_items (list[dict[str, Any]]): line items.
    """
    receiver_email = "jalin.howard@gmail.com"
    message = MIMEMultipart("alternative")
    message["Subject"] = "XBot Success Report"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(message["Subject"], "plain")
    part2 = MIMEText(
        f"""/
        <div>
        {''.join(['<p>https://www.x.com/%s/status/%s</p>' % (u,i) for u,i in success])}
        </div>
        """,
        "html",
    )

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    server = smtplib.SMTP_SSL("smtp.gmail.com")
    server.login(sender_email, password)
    server.ehlo()
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.close()


class LocalUnixDict:
    hash: dict[str, bool | str]
    epoch: int

    def __init__(self) -> None:
        if os.path.isfile(VISITED_HASH_PATH):
            with open(
                VISITED_HASH_PATH, "r+", encoding="utf-8"
            ) as file:
                self.hash = json.load(file)
                self.epoch = int(self.hash["epoch"])
        else:
            with open(
                VISITED_HASH_PATH, "w+", encoding="utf-8"
            ) as filehandler:
                self.epoch = int(time.time())
                self.hash = {"epoch": f"{self.epoch}"}
                json.dump(self.hash, filehandler, indent=4)

    def __update(self) -> None:
        with open(
            VISITED_HASH_PATH, "w+", encoding="utf-8"
        ) as filehandler:
            json.dump(self.hash, filehandler, indent=4)

    def write(
        self,
        _id: str,
        _time: float,
        callback: Callable[[], None] | None,
    ) -> None:

        _exists = True if self.hash.get(_id, False) else False

        if not _exists and _time > self.epoch:
            try:
                if callback:
                    callback()
                self.hash.update({_id: True})
                self.__update()
            except:
                raise Exception(  # pylint: disable=broad-exception-raised
                    "Write Callback failed. Aborting cache write..."
                )
        elif _exists:

            logging.debug("Reply id:%s exists", _id)
            raise Exception(  # pylint: disable=broad-exception-raised
                "Reply exists."
            )
        else:
            logging.debug(
                "Reply id:%s\ndate:%s is too far in past",
                _id,
                time_to_string(_time),
            )
            raise Exception(  # pylint: disable=broad-exception-raised
                "Reply in the past."
            )


class XBot:
    chrome: webdriver.Firefox
    cache: LocalUnixDict

    def __init__(self, users: list[str]) -> None:
        self.cache = LocalUnixDict()

        # Open X for Auth
        self.__open_chrome()

        # Gather Tweets/Replys
        # Check against cache to see if anything is new
        tweets_tdy = []
        for u in users:
            tweets_tdy += self.get_recent(u)

        # Reload chrome window
        self.__open_chrome()

        success_report = []

        # Post reply to all recent tweets
        for tw, tt in tweets_tdy:
            try:
                tw.replace("/", " ")
                user, status_id = (
                    re.sub(r"\/status\/", ",", tw)
                    .replace("/", "")
                    .split(",")
                )

                self.cache.write(
                    status_id,
                    tt,
                    lambda: self.__post_reply(
                        user,
                        status_id,
                        "Kamala Sues MyLeft.org over AI generated image!",
                    ),
                )
                success_report.append((user, status_id))
            except Exception:
                logging.debug(
                    "Failed to post reply user: %s\nid: %s\n time: %s",
                    user,
                    status_id,
                    time_to_string(tt),
                )

        self.chrome.quit()
        send_report(success_report)

    def __open_chrome(self) -> None:
        """Create Headless Chrome

        Returns:
            webdriver.Firefox: Headless Chrome Driver

        Raises:
            e: Error starting chrome
        """
        try:
            if getattr(self, "chrome", None):
                self.chrome.quit()
            chrome_options = webdriver.FirefoxOptions()

            chrome_options.add_argument("disable-infobars")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-dev-shm-usage")

            if ENV != "development":
                chrome_options.add_argument("headless")
                chrome_options.add_argument(
                    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
                )
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_experimental_option(
                "excludeSwitches", ["enable-automation"]
            )

            # Disable password manager
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
            }

            chrome_options.add_experimental_option("prefs", prefs)

            # Remote debugging to prevent Chrome from detecting automation
            chrome_options.add_argument(
                "--remote-debugging-port=9222"
            )

            driver = webdriver.Firefox(
                service=service, options=chrome_options
            )
            self.chrome = driver
            driver.get(HOME)

            for cookie in self.get_auth():
                driver.add_cookie(cookie)

            driver.refresh()

            try:
                WebDriverWait(self.chrome, TIMEOUT).until(
                    EC.visibility_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            "a[href$='login']",
                        )
                    )
                )
                self.__login()
            except TimeoutException:
                logging.debug("Logged in successfully.")
                self.__save_auth()

        except Exception as e:
            logging.debug("Error starting chrome: %e", e)
            raise e from Exception("Error starting chrome.")

    def __save_auth(self) -> None:
        """Save Auth Cookies"""
        try:
            WebDriverWait(self.chrome, TIMEOUT).until(
                EC.invisibility_of_element_located(
                    (
                        By.XPATH,
                        "//div[@role='progressbar']",
                    )
                )
            )

            cookies = self.chrome.get_cookies()
            cookies = [
                *filter(
                    lambda a: a.get("name") == "auth_token", cookies
                )
            ]

            if len(cookies) < 1:
                raise KeyError("Unable to locate auth token.")

            with open(AUTH_COOKIE, "wb+") as filehandler:
                pickle.dump(cookies, filehandler)
        except TimeoutException:
            logging.debug("Driver timed out saving auth_token.")
            raise TimeoutException(
                "Driver timed out saving auth_token."
            )

    def get_auth(self) -> list[dict[Any, Any]]:
        """Get Auth Cookies from File"""
        if Path(AUTH_COOKIE).is_file():
            with open(AUTH_COOKIE, "rb") as cookiesfile:
                cookies: list[dict[Any, Any]] = pickle.load(
                    cookiesfile
                )

                return [
                    *filter(
                        lambda x: x["name"] == "auth_token", cookies
                    )
                ]
        return []

    def __login(self) -> None:

        self.chrome.get("https://x.com/i/flow/login")

        username = WebDriverWait(self.chrome, TIMEOUT).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'input[autocomplete="username"]')
            )
        )
        username.send_keys(UNAME)
        username.send_keys(Keys.ENTER)

        password = WebDriverWait(self.chrome, TIMEOUT).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'input[name="password"]')
            )
        )

        password.send_keys(PWORD)
        password.send_keys(Keys.ENTER)

        self.__save_auth()

    def get_recent(self, user: str) -> list[tuple[str, float]]:
        """Get recent status ID's

        Args:
            uname (str): _description_
            feed (str, optional): _description_. Defaults to "/".

        Returns:
            _type_: _description_
        """
        self.__open_chrome()
        with self.chrome as browser:
            browser.get("https://x.com/%s" % (user))

            replies_tab = WebDriverWait(browser, TIMEOUT).until(
                EC.visibility_of_element_located(
                    (By.XPATH, f"//a[@href='/{user}/with_replies']")
                )
            )

            tweet_soup = BeautifulSoup(
                browser.page_source, features="html.parser"
            )

            replies_tab.click()
            try:

                WebDriverWait(browser, TIMEOUT).until(
                    EC.invisibility_of_element_located(
                        (
                            By.XPATH,
                            "//div[@role='progressbar']",
                        )
                    )
                )
            except TimeoutException:
                logging.debug(
                    "Page load timeout, while getting recent tweets."
                )
                raise TimeoutException(
                    "Page load timeout, while getting recent tweets."
                )

            reply_soup = BeautifulSoup(
                browser.page_source, features="html.parser"
            )

            def valid_status_link(
                acc: tuple[list[str], list[str]],
                elems: tuple[Any, Any],
            ) -> tuple[list[str], list[str]]:
                ref, _time = elems

                if _time is not None:

                    return sorted(  # type: ignore[return-value]
                        [
                            *acc,
                            [ref, _time],
                        ],
                        key=lambda x: x[1],
                        reverse=True,
                    )

                return acc

            links = [
                (
                    link["href"],
                    (
                        lambda t: (
                            datetime.datetime.strptime(
                                t,
                                "%Y-%m-%dT%H:%M:%S.%fZ",
                            )
                            - datetime.datetime(1970, 1, 1)
                        ).total_seconds()
                        if t is not None
                        else None
                    )(link.find("time").get("datetime", None)),
                )
                for link in [
                    *tweet_soup.find_all(
                        "a",
                        href=re.compile(rf"^\/{user}\/status\/\d+$"),
                    ),
                    *reply_soup.find_all(
                        "a",
                        href=re.compile(rf"^\/{user}\/status\/\d+$"),
                    ),
                ]
            ]

            get_links = reduce(valid_status_link, links, ())  # type: ignore[arg-type]

            return get_links  # type: ignore[return-value]

    def __post_reply(
        self,
        user: str,
        status_id: str,
        body: str,
    ) -> None:
        """Reply to Tweet

        Args:
            user (str): username
            status_id (str): status id
            body (str): body of tweet
        """
        with self.chrome as browser:
            self.chrome = browser

            url = "https://x.com/" + user + "/status/" + status_id
            browser.get(url)

            try:

                WebDriverWait(browser, TIMEOUT).until(
                    EC.invisibility_of_element_located(
                        (
                            By.XPATH,
                            "//div[@role='progressbar']",
                        )
                    )
                )
            except TimeoutException:
                logging.debug(
                    "Page load timeout, while getting posting reply."
                )
                raise TimeoutException(
                    "Page load timeout, while getting posting reply."
                )

            reply_button = browser.find_element(
                By.XPATH,
                "//div[@data-testid='tweetTextarea_0RichTextInputContainer']",
            )

            reply_button.click()

            try:
                text_area = browser.find_element(
                    By.XPATH, "//div[@data-testid='tweetTextarea_0']"
                )

                text_area.send_keys(
                    body
                    if user != "elonmusk"
                    else "Hey Elon,\nLaid off engineer in the Kamaleconomy, help me sell 1000 cans of Cashews from the great red state of Oklahoma! https://www.myleft.org"
                )

                file_input = browser.find_element(
                    By.XPATH, "//input[@type='file']"
                )

                file_input.send_keys(
                    CLICK_BAIT_PATH + "\n" + PRODUCT_IMG_PATH
                    if user != "elonmusk"
                    else PRODUCT_IMG_PATH
                )

                def find_upload(d: webdriver.Firefox) -> bool:
                    imgs = d.find_elements(By.TAG_NAME, "img")
                    for i in imgs:
                        img_src = i.get_attribute("src") or ""

                        if re.match(r"^blob:.+", img_src) is not None:
                            return True
                    return False

                try:
                    WebDriverWait(self.chrome, TIMEOUT).until(
                        find_upload
                    )
                    send_button = browser.find_element(
                        By.XPATH,
                        "//button[@data-testid='tweetButtonInline']",
                    )

                    send_button.click()

                    time.sleep(5)
                    logging.debug(
                        "Posted reply %s/%s", user, status_id
                    )
                except TimeoutException:
                    e_msg = "Failed to attach media."
                    logging.debug(e_msg)
                    raise TimeoutException(e_msg)

            except Exception as e:
                logging.debug(
                    "Failed to post reply.\nStatus Id: %s\nURL: https://www.x.com/%s/status/%s",
                    status_id,
                    user,
                    status_id,
                )
                raise e


x = XBot(["myleftsnuts"])
#     [
#         "elonmusk",
#         "DonaldTNews",
#         "GOP",
#         "nbcsnl",
#         "AB84",
#         "DonaldJTrumpJr",
#         "JDVance",
#         "mayemusk",
#         "KamalaHarris",
#         "alexandrosM",
#         "RepMTG",
#         "laurenboebert",
#         "benshapiro",
#         "SenTedCruz",
#         "joerogan",
#         "RealCandaceO",
#         "realDonaldTrump",
#         "TeamTrump",
#         "stclairashley",
#         "iamcardib",
#         "itsdeaann",
#     ]
# )
