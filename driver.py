from selenium import webdriver
import time


class Driver:

    # connect to driver
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.get("http://cappa.csu.ru/")
        self.driver.find_element("class name", "profile__bar-login").click()
        time.sleep(1)

    def get(self):
        return self.driver

    def find_element(self, type_, value_):
        return self.driver.find_element(type_, value_)

    def find_elements(self, type_, value_):
        return self.driver.find_elements(type_, value_)

    def close(self):
        self.driver.close()
