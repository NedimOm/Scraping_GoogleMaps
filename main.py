import logging
from scraping import scrape
from filtering import filter_urls

logging.basicConfig(
    handlers=[
        logging.FileHandler('scraping_and_filtering_websites.log'),
        logging.StreamHandler()
    ],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    scrape()
    filter_urls()
