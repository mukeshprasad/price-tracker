TABLE_NAME = "product_details"
URL_PATTERN = r"https?://\S+"
DB_URL = "postgresql+psycopg2://dev:admin@localhost/dropalertbot"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US, en;q=0.5",
}

INTRO_MESSAGE = (
    "Hello and Welcome to MP's PriceDropAlertBot!!\n\n"
    "Enter product url which you would like to track."
)

UPDATE_MESSAGE = """Price Dropped by {difference}!!
{product_title}
{product_url}
New Price: {market_price}
"""

LIST_MESSAGE = """
{idx}. {product_name}
{product_url}
"""

EMPTY_LIST_MESSAGE = "No products being tracked."
STD_500_MESSAGE = "Something went wrong, please try again later."
