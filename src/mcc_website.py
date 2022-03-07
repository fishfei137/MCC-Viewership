from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException, TimeoutException
import logging
import os
import now_bst
import error_alert

now = now_bst.now()

base_url = 'https://mcc.live'

driver_path = os.environ.get('chrome_driver_path')
s = Service(driver_path)
options = Options()
options.add_argument('--headless')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(service = s, options=options)
driver.get(base_url)


def get_game():
    try:
        game_xpath = '/html/body/div/div[4]/div/div[2]/div/div/div/div/span/span/h2'

        game = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, game_xpath))).text
        logging.info(f"{now} game found {game}")
#(ElementNotVisibleException, NoSuchElementException, TimeoutException)
    except:
        game = ''
        logging.warning(f"{now} game not found")
        error_alert.tele_notify('*Game not found*')
    return game
#driver.quit()
