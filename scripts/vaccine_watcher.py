import re
import time
from re import search

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions
from bs4 import BeautifulSoup
import telegram

from scripts.defs import *
from scripts.point import Point
from scripts.vaccine_parser import VaccineStatus, vaccine_status_parser


class VaccineWatcher(object):
    def __init__(self, bound1: Point, bound2: Point, search_interval: float=1.5, notify_interval: float=60):
        self.bound1 = bound1
        self.bound2 = bound2
        self.notified_orgs = {}
        driver_config = webdriver.ChromeOptions()
        driver_config.headless = True
        self.driver = webdriver.Chrome(options=driver_config)
        self.search_interval = search_interval
        self.notify_interval = notify_interval
        self.telegram_bot = telegram.Bot(TELEGRAM_BOT_TOKEN)

    def run_search(self):
        try:
            while True:
                start_time = time.time()
                search_url = URL_TEMPLATE.format(
                    cpx=(self.bound1.x + self.bound2.x) / 2, cpy=(self.bound1.y + self.bound2.y) / 2,
                    b1x=self.bound1.x, b1y=self.bound1.y,
                    b2x=self.bound2.x, b2y=self.bound2.y
                )
                self.driver.get(search_url)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "WRzCS"))
                )
                
                list_div = self.driver.find_element_by_class_name("WRzCS")
                list_items = list_div.find_elements_by_class_name("_1mrr7")

                for item in list_items:
                    vaccine_status = vaccine_status_parser(BeautifulSoup(item.get_attribute("innerHTML"), "lxml"))
                    reservation_url = search_url + "&selected_place_id={code:s}".format(code=vaccine_status.org_code)
                    print(vaccine_status)
                    print("Org Link: " + reservation_url)
                    print()
                    self.update_notification(vaccine_status=vaccine_status, reservation_url=reservation_url)

                end_time = time.time()
                diff_time = end_time - start_time
                if diff_time < self.search_interval:
                    time.sleep(self.search_interval - diff_time)

        finally:
            self.driver.quit()
    
    def update_notification(self, vaccine_status: VaccineStatus, reservation_url: str):
        current_time = time.time()
        if vaccine_status.org_code in self.notified_orgs:
            notified_time = self.notified_orgs[vaccine_status.org_code]
            if vaccine_status.status in STATUS_TO_IGNORE:
                if current_time - notified_time > self.notify_interval:
                    self.notified_orgs.pop(vaccine_status.org_code)
            else:
                if current_time - notified_time > self.notify_interval:
                    self.send_notification(vaccine_status=vaccine_status, reservation_url=reservation_url)
                    self.notified_orgs[vaccine_status.org_code] = current_time
        else:
            if vaccine_status.status not in STATUS_TO_IGNORE:
                self.send_notification(vaccine_status=vaccine_status, reservation_url=reservation_url)
                self.notified_orgs[vaccine_status.org_code] = current_time
    
    def send_notification(self, vaccine_status: VaccineStatus, reservation_url: str):
        message = "아래 기관에서 상태 변화가 감지되었습니다. \n"
        message += vaccine_status.__str__()
        print("Alerting recipient...")
        message += "\n예약 URL: " + reservation_url
        self.telegram_bot.sendMessage(chat_id=TELEGRAM_RECIPIENT_ID, text=message)

if __name__ == "__main__":
    bounds_string = "126.8156015%3B37.5301225%3B126.8845236%3B37.5682981"
    bounds = [float(x) for x in bounds_string.split("%3B")]
    watcher = VaccineWatcher(bound1=Point(bounds[0], bounds[1]), bound2=Point(bounds[2], bounds[3]))
    watcher.run_search()