# -*- coding: utf-8 -*-
import os
import sys
from typing import List
from selenium import webdriver

from configuration import Configuration
from models.product import Product
from services.avito_block_service import AvitoBlockService

__author__ = 'CoderGosha'
import logging
# from grab import Grab
from webdriver_manager.chrome import ChromeDriverManager


def chrome_options():
    configuration = Configuration()
    proxy = configuration.config['PROXY']

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('no-sandbox')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('enable-automation')
    options.add_argument('disable-infobars')
    options.add_argument('disable-gpu')
    options.add_argument('disable-browser-side-navigation')
    options.add_argument('dns-prefetch-disable')
    options.add_argument('log-level=3')
    # options.add_argument('proxy-server=%s' % "localhost:8118")
    if proxy:
        options.add_argument('--proxy-server=socks5://' + proxy)
    return options


class AvitoParsing:
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options())

    def __init__(self, start_url, id_parser, block_service):
        self.StartUrl = start_url
        self.ResultElement = []
        self.IdParser = id_parser
        import logging
        from selenium.webdriver.remote.remote_connection import LOGGER
        LOGGER.setLevel(logging.INFO)
        self.block_service = block_service

    def parsing_start(self)->List[Product]:
        if self.block_service.is_parsing():
            return self._parsing_catalog_auto()

        return []

    def _parsing_catalog_auto(self)->List[Product]:
        self.ResultElement = []

        self.driver.set_page_load_timeout(30)
        self.driver.set_script_timeout(30)
        self.driver.implicitly_wait(10)

        try:
            # load the desired webpage
            self.driver.get(self.StartUrl)
            try:
                self.driver.find_element_by_class_name("icon-forbidden")
                self.block_service.add_block()
                return []
            except:
                pass

            for entry in self.driver.find_elements_by_xpath('//div[@itemtype="http://schema.org/Product"]'):
                link = entry.find_element_by_xpath('.//a[@itemprop="url"]').get_attribute("href")
                # description = entry.find_element_by_xpath('.//a[@itemprop="url"]').get_attribute("title")
                # description += ", %s" % entry.find_element_by_xpath('.//span[@itemtype="http://schema.org/Offer"]').text
                description = entry.text

                if len(link) > 1:
                    self.ResultElement.append(Product(url=link, description=description, parser_id=self.IdParser))
                    logging.debug('%s, %s' % (description, link))
                if len(self.ResultElement) > 10:
                    break

        except Exception as ex:
            logging.error(ex)

        finally:
            pass
            #driver.close()
            #driver.quit()

        logging.info('Parsing completed: %s - %i' % (self.StartUrl, len(self.ResultElement)))
        return self.ResultElement




def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = AvitoParsing('http://www.avito.ru/vologodskaya_oblast/avtomobili/vaz_lada/largus-ASgBAgICAkTgtg3GmSjitg2KqSg?cd=1&pmax=500000', 1)
    result = parser.parsing_start()
    if result is not None:
        print(len(result))


if __name__ == "__main__":
    main()
