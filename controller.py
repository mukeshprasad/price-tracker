from sqlalchemy.sql import text
from datetime import datetime
from amzn import ScrapeAmazon
from helpers import *
from db_utils import DBUtils
from constants import *


class Controller:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_tracker_response(bot):
        try:
            db_session = DBUtils.get_db_session()
            start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"started tracking at: {start_time}")
            query = f"SELECT * FROM {TABLE_NAME}"
            data = db_session.execute(text(query)).fetchall()
            for record in data:
                product_url, current_price_string = (
                    record.product_url,
                    record.current_price,
                )
                product_name, id_, user_id = (
                    record.product_name,
                    record.id,
                    record.user_id,
                )
                current_price = float(current_price_string)
                scraper = ScrapeAmazon(url=product_url)
                market_price_string = scraper.get_price()
                market_price = float(market_price_string[1:])
                difference = current_price - market_price
                if market_price >= current_price:
                    continue
                update_query = f"UPDATE {TABLE_NAME} SET current_price = {market_price} WHERE id={id_}"

                db_session.execute(text(update_query))
                db_session.commit()
                update_msg = UPDATE_MESSAGE.format(
                    difference=difference,
                    product_title=product_name,
                    product_url=product_url,
                    market_price=market_price_string,
                )
                bot.send_message(user_id, update_msg)
        except Exception as e:
            print("Error occurred in {get_tracker_response}:", e)
        finally:
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Stopped tracking at: {end_time}")
            if db_session:
                db_session.close()

    @staticmethod
    def get_tracking_list(message):
        try:
            db_session = DBUtils.get_db_session()
            user_id = message.from_user.id
            list_query = (
                f"SELECT * FROM {TABLE_NAME} WHERE user_id='{user_id}' ORDER BY id"
            )
            result = db_session.execute(text(list_query)).fetchall()
            product_list = []
            for idx, record in enumerate(result, start=1):
                product_list.append(
                    LIST_MESSAGE.format(
                        idx=idx,
                        product_name=record.product_name,
                        product_url=record.product_url,
                    )
                )
            if product_list:
                msg = (
                    "\n".join(product_list)
                    + "\n To stop tracking a product, use /untrack"
                )
            else:
                msg = EMPTY_LIST_MESSAGE
            return len(product_list), msg
        except Exception as e:
            print("Error occurred in {get_tracking_list}:", e)
            return 0, STD_500_MESSAGE
        finally:
            if db_session:
                db_session.close()

    @staticmethod
    def tracking_list_count(message):
        db_session = DBUtils.get_db_session()
        user_id = message.from_user.id
        count_query = f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE user_id='{user_id}'"
        count = db_session.execute(text(count_query)).fetchone()[0]
        db_session.close()
        return count

    @staticmethod
    def untrack_product(message):
        try:
            db_session = DBUtils.get_db_session()
            user_id = message.from_user.id
            custom_id = message.text.split("_")[1]
            if custom_id.isdigit() and int(custom_id) > 0:
                custom_id = int(custom_id)
                pid_query = f"SELECT id FROM {TABLE_NAME} WHERE user_id='{user_id}' OFFSET {custom_id-1} LIMIT 1"
                pid = db_session.execute(text(pid_query)).fetchone()
                if not pid:
                    return f"No Product with ID: {custom_id}"
                else:
                    pid = pid[0]
            else:
                return f"Invalid ID: {custom_id}"
            delete_query = f"DELETE FROM {TABLE_NAME} WHERE id={pid}"
            db_session.execute(text(delete_query))
            db_session.commit()
            return f"Product with ID {custom_id} has been untracked."
        except Exception as e:
            print("Error occurred in {untrack_product}:", e)
            return STD_500_MESSAGE
        finally:
            if db_session:
                db_session.close()

    @staticmethod
    def run(message):
        try:
            track_count = Controller.tracking_list_count(message)
            if track_count == 10:
                return "You can track up to 10 Products only.\nHint: Untrack products you no longer need\nView /list here."
            sender_info = message.from_user
            sender_text = message.text
            url_exist, url = get_url_from_message(sender_text)
            response = ""
            if url_exist:
                platform = get_platform(url)
                if platform in ["amazon", "amzn"]:
                    scraper = ScrapeAmazon(url=url, sender_info=sender_info)
                    response = scraper.process()
                else:
                    response = "Only Amazon Products are supported. Other platforms coming soon!! 😉"
            else:
                response = (
                    "Arey bhai bhai! Yeh kya send kar diya 😒. Yeh nahi chahiye na 🙂"
                )
            return response
        except Exception as e:
            print("Error occurred:", e)
            return STD_500_MESSAGE
