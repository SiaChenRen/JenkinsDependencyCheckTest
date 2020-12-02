import sys, os
import time

import flask

myPath = os.path.dirname(os.path.abspath(__file__))
abc = sys.path.insert(0, myPath + '/../')

import unittest
from flask import Flask
from flask_testing import LiveServerTestCase
from app import create_app

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class Test(LiveServerTestCase):

    def create_app(self):
        app = create_app()
        app.config.update(
            LIVESERVER_PORT=8943
        )
        return app

    def setUp(self):
        # setup flask app
        app = create_app()
        self.app = app.test_client()

        # setup chromedriver
        opts = Options()
        opts.add_argument("--no-sandbox")
        opts.add_argument("--headless")
        opts.add_argument("window-size-1920,1080")
        opts.add_argument("start-maximized")
        opts.add_argument("disable-gpu")
        opts.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=opts)
        self.driver.get(self.get_server_url())

    def tearDown(self):
        self.driver.quit()

    def test_login_valid(self):
        self.driver.get(self.get_server_url() + "/")
        self.driver.find_element_by_name("password").send_keys("asdasdasd")

        loginButton = "body > form > input[type=submit]:nth-child(4)"
        self.driver.find_element_by_css_selector(loginButton).click()
        assert "Log Out" in self.driver.page_source


    def test_logout_valid(self):
        self.driver.get(self.get_server_url() + "/")

        logoutButton = "body > form > input[type=submit])"
        self.driver.find_element_by_css_selector(logoutButton).click()
        assert "Submit" in self.driver.page_source

  


if __name__ == '__main__':
    unittest.main()
