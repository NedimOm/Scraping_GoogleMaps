import yaml
import sys
import time
import logging
import pandas as pd
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchWindowException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

with open("config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)


def configure_driver():
    """
    Configures driver for scraping Google Chrome
    :return: configured driver
    """
    logging.info("Configuring the Chrome driver.")

    chrome_options = webdriver.ChromeOptions()

    chrome_options.add_argument("--headless")

    driver_to_return = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    logging.info("Chrome driver configured successfully.")
    return driver_to_return


def facility_entry(driver, search_query):
    """
    Enters name & address of facility into Google Maps
    :param driver: driver for scraping Google Chrome
    :param search_query: name & address of facility
    """
    logging.info(f"Entering search query: {search_query}")
    WebDriverWait(driver, 5).until(
        ec.presence_of_element_located((By.CLASS_NAME, "xiQnY"))
    )
    input_element = driver.find_element(By.CLASS_NAME, "xiQnY")
    input_element.send_keys(search_query + Keys.ENTER)


def scroll_sidebar(driver):
    """
    Moves mouse pointer to sidebar and scrolls it
    :param driver: driver for scraping Google Chrome
    """
    logging.info("Scrolling the sidebar.")
    WebDriverWait(driver, 5).until(
        ec.presence_of_element_located((By.CLASS_NAME, "DkEaL"))
    )
    element_to_hover = driver.find_element(By.CLASS_NAME, "DkEaL")
    ActionChains(driver).move_to_element(element_to_hover).perform()

    for i in range(10):
        element_to_hover.send_keys(Keys.PAGE_DOWN)


def switch_to_frame(driver):
    """
    Switching to iframe because clickable elements are in it
    :param driver: driver for scraping Google Chrome
    """
    logging.info("Switching to the iframe.")
    WebDriverWait(driver, 5).until(
        ec.presence_of_element_located((By.CLASS_NAME, "rvN3ke"))
    )
    frame = driver.find_element(By.CLASS_NAME, 'rvN3ke')
    driver.switch_to.frame(frame)


def get_urls_from_web_search(driver):
    """
    Opens websites from web search, then gets their urls
    :param driver: driver for scraping Google Chrome
    :return: array containing 3 urls of websites from web search
    """
    logging.info("Extracting URLs from the web search.")
    WebDriverWait(driver, 5).until(
        ec.presence_of_element_located((By.CLASS_NAME, "rCjKj"))
    )

    array_of_urls = []
    elements_with_links = driver.find_elements(By.CLASS_NAME, "rCjKj")

    for element in elements_with_links:
        driver.execute_script("arguments[0].click();", element)

    main_window_handle = driver.current_window_handle
    all_windows = driver.window_handles
    for handle in all_windows:
        if handle != main_window_handle:
            driver.switch_to.window(handle)
            time.sleep(1)
            new_tab_url = driver.current_url
            array_of_urls.append(new_tab_url)
            logging.info(f"Extracted URL: {new_tab_url}")
            driver.close()
            driver.switch_to.window(main_window_handle)

    return array_of_urls


def scrape():
    """
    Scraping urls from Google Maps web search for every facility from .csv file
    """
    logging.info("Starting the scraping process.")
    driver = configure_driver()

    facilities_with_err_html_noweb_df = pd.read_csv(cfg['facilities_with_err_html_noweb'])

    possible_websites = []

    for index, row in facilities_with_err_html_noweb_df.iterrows():
        facility_name = row['qname']
        facility_address = row['formatted_address']

        search_query = f"{facility_name}, {facility_address}"
        driver.get(cfg['scraping_site'])

        try:
            facility_entry(driver, search_query)

            time.sleep(1)

            scroll_sidebar(driver)

            switch_to_frame(driver)

            array_of_urls = get_urls_from_web_search(driver)

            time.sleep(1)

            possible_websites.append(array_of_urls)
        except TimeoutException:
            logging.error(f"TimeoutException occurred for search query: {search_query}")
            possible_websites.append("NULL")
        except NoSuchWindowException:
            logging.error("NoSuchWindowException: Browser window was closed unexpectedly.")
            driver.quit()
            sys.exit(1)
        except WebDriverException:
            logging.error("WebDriverException occurred, quitting driver.")
            driver.quit()
            sys.exit(1)
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            driver.quit()
            sys.exit(1)

    facilities_with_err_html_noweb_df['possible_website'] = possible_websites

    output_file = cfg['facilities_with_possible_web']
    facilities_with_err_html_noweb_df.to_csv(output_file, index=False)
    logging.info(f"Scraping process completed. Results saved to {output_file}.")

    driver.quit()
