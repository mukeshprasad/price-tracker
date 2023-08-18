import requests
from pprint import pprint
from bs4 import BeautifulSoup
from db_utils import DBUtils
from constants import TABLE_NAME
from helpers import get_soup
from sqlalchemy.sql import text


class ScrapeAmazon:
    def __init__(self, data=None, url=None, sender_info=None):
        self.data = data
        self.url = url
        self.sender_info = sender_info
        self.db_session = DBUtils.get_db_session()

    def get_title(self):
        try:
            if not self.data:
                self.data = get_soup(self.url)
            title = self.data.find("span", attrs={"id": "productTitle"})
            title_value = title.string
            title_string = title_value.strip()
            return title_string
        except Exception as e:
            print("Error occurred in {record_already_exist}:", e)
            title_string = ""
        return title_string

    def get_price(self):
        try:
            # price = soup.find("span", class_=["a-price-symbol", "a-price-whole"])
            if not self.data:
                self.data = get_soup(self.url)
            symbol = self.data.find("span", class_="a-price-symbol").string.strip()
            price = self.data.find("span", class_="a-price-whole").get_text()
            decimal = self.data.find("span", class_="a-price-fraction").get_text()
            price_ = symbol + price + decimal
            print("price:", price_)
        except Exception as e:
            print("Error occurred in {get_price}:", e)
            price_ = ""
        return price_

    def get_rating(self):
        try:
            rating = self.data.find(
                "i", attrs={"class": "a-icon a-icon-star a-star-4-5"}
            ).string.strip()
        except AttributeError:
            try:
                rating = self.data.find(
                    "span", attrs={"class": "a-icon-alt"}
                ).string.strip()
            except:
                rating = ""
        return rating

    def get_review_count(self):
        try:
            review_count = self.data.find(
                "span", attrs={"id": "acrCustomerReviewText"}
            ).string.strip()
        except AttributeError:
            review_count = ""

        return review_count

    def get_availability(self):
        try:
            available = self.data.find("div", attrs={"id": "availability"})
            available = available.find("span").string.strip()
        except AttributeError:
            available = ""
        return available

    def record_already_exist(self, name, price):
        try:
            user_id, username = self.sender_info.id, self.sender_info.username
            product_name, product_url = name, self.url
            query = f"""SELECT 1 FROM {TABLE_NAME} WHERE user_id='{user_id}' 
                    AND product_url='{product_url}' AND product_name='{product_name}'
                    """
            result = self.db_session.execute(text(query)).fetchone()
            print(result)
            return True if result else False
        except Exception as e:
            print("Error occurred in {record_already_exist}:", e)
            return False

    def add_record(self, name, price):
        try:
            user_id, username = self.sender_info.id, self.sender_info.username
            product_name, product_url = name, self.url
            current_price, new_price = float(price[1:]), None
            platform = "Amazon"
            query = f"""INSERT INTO {TABLE_NAME} 
                    (user_id, username, product_url, product_name, current_price, platform) VALUES 
                    ('{user_id}', '{username}', '{product_url}', '{product_name}', {current_price}, '{platform}')
                    """
            self.db_session.execute(text(query))
            self.db_session.commit()
            print("Successfully added record")
        except Exception as e:
            print("Error occurred in {add_record}:", e)
            print("adding record failed")

    def process(self):
        try:
            self.data = get_soup(self.url)
            title, price = self.get_title(), self.get_price()
            if title in ["", None] or price in ["", None]:
                return "Uh-oh! We couldn't find the product or the URL seems invalid. Please check the link and try again."
            response = f"{title}\n" f"Current Price: {price}\n"
            if self.record_already_exist(title, price):
                response = "\n\nProduct already being tracked. View your /list here."
            else:
                self.add_record(title, price)
                response += (
                    "\n\nYay!!Your request has been placed. It is being tracked."
                    "\nYou will receive a notification when there is a drop in its price."
                )
            print(response)
            return response
        except Exception as e:
            print(f"Error occured in {self.__class__.__name__}.process:", e)
            return ""
        finally:
            if self.db_session:
                self.db_session.close()
