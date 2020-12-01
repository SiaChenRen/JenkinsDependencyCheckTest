import sys, os
import time

import flask

myPath = os.path.dirname(os.path.abspath(__file__))
abc = sys.path.insert(0, myPath + '/../')

import unittest
import urllib.request
import random

from flask import Flask
from flask_testing import LiveServerTestCase
from app import create_app
from app.db import DB
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
        app.config.from_object('config.TestingConfig')
        self.app = app.test_client()
        with app.app_context():
            from app.ocr import Tesseract
            self.Tesseract = Tesseract()

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

    def test_server_is_up_and_running(self):
        response = urllib.request.urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)

    def test_login_valid(self):
        self.driver.get(self.get_server_url() + "/auth/login")
        self.driver.find_element_by_name("email").send_keys("test@gmail.com")
        self.driver.find_element_by_name("password").send_keys("testing123")

        loginButton = "#top > div > section.site-section > div > div > div > form > div:nth-child(4) > div > input.btn.px-4.btn-primary.text-white"
        # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, loginButton)))

        self.driver.find_element_by_css_selector(loginButton).click()
        assert "Log out" in self.driver.page_source

    def test_login_invalid(self):
        self.driver.get(self.get_server_url() + "/auth/login")
        self.driver.find_element_by_name("email").send_keys("test@gmail.com")
        self.driver.find_element_by_name("password").send_keys("invalid_password_input")

        loginButton = "#top > div > section.site-section > div > div > div > form > div:nth-child(4) > div > input.btn.px-4.btn-primary.text-white"
        # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, loginButton)))

        self.driver.find_element_by_css_selector(loginButton).click()
        assert "Invalid Email/Password" in self.driver.page_source

    def test_login_invalid_email(self):
        self.driver.get(self.get_server_url() + "/auth/login")
        self.driver.find_element_by_name("email").send_keys("test@gmail.com")
        self.driver.find_element_by_name("password").send_keys("invalid_password_input")

        loginButton = "#top > div > section.site-section > div > div > div > form > div:nth-child(4) > div > input.btn.px-4.btn-primary.text-white"
        # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, loginButton)))

        self.driver.find_element_by_css_selector(loginButton).click()
        assert "Please enter a valid email address" in self.driver.page_source

    def test_login_invalid_password(self):
        self.driver.get(self.get_server_url() + "/auth/login")
        self.driver.find_element_by_name("email").send_keys("test@gmail.com")
        self.driver.find_element_by_name("password").send_keys("invalid_password_input")

        loginButton = "#top > div > section.site-section > div > div > div > form > div:nth-child(4) > div > input.btn.px-4.btn-primary.text-white"
        # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, loginButton)))

        self.driver.find_element_by_css_selector(loginButton).click()
        assert "Your password must be at least 8 characters long" in self.driver.page_source

    def test_logout(self):
        # login first
        self.driver.get(self.get_server_url() + "/auth/login")
        self.driver.find_element_by_name("email").send_keys("test@gmail.com")
        self.driver.find_element_by_name("password").send_keys("testing123")

        loginButton = "#top > div > section.site-section > div > div > div > form > div:nth-child(4) > div > input.btn.px-4.btn-primary.text-white"
        # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, loginButton)))

        self.driver.find_element_by_css_selector(loginButton).click()

        # logout
        self.driver.get(self.get_server_url() + "/auth/logout")
        self.assertEqual(self.driver.current_url, self.get_server_url() + "/")

    def test_register(self):
        email = "testregisteremail%d@test.com" % (random.randint(0, 999))
        self.driver.get(self.get_server_url() + "/auth/register")
        self.driver.find_element_by_name("email").send_keys(email)
        self.driver.find_element_by_name("password").send_keys("testing456ab")
        self.driver.find_element_by_name("confirmpassword").send_keys("testing456ab")
        self.driver.find_element_by_name("register").click()

        # remove created user
        db = DB()
        cursor = db.cursor()

        sql = "SELECT account_id FROM accounts WHERE email=%s"
        cursor.execute(sql, (email,))
        user_id = cursor.fetchone()["account_id"]

        db.mysql.delete_token(user_id, "verify account")

        try:
            cursor = db.cursor()
            sql = "DELETE FROM accounts WHERE account_id=%s"
            cursor.execute(sql, (user_id,))
            db.mysql.db.commit()
        except:
            pass

        assert "Account has been successfully created" in self.driver.page_source


    def test_create_post(self):
        # login first
        self.driver.get(self.get_server_url() + "/auth/login")
        self.driver.find_element_by_name("email").send_keys("test@gmail.com")
        self.driver.find_element_by_name("password").send_keys("testing123")
        self.driver.find_element_by_name("login").click()

        self.driver.get(self.get_server_url() + "/post/create-post")
        self.driver.find_element_by_name("post-title").send_keys("Sec3Math")
        self.driver.find_element_by_name("post-description").send_keys("linearequation")
        self.driver.find_element_by_name("post-content").send_keys("testingnow")
        self.driver.find_element_by_name("submitpost").click()
        assert "Post has been successfully created" in self.driver.page_source

    def test_search_post(self):
        # search directly from main page
        self.driver.get(self.get_server_url())
        self.driver.find_element_by_name("search").send_keys("sec")
        self.driver.find_element_by_name("searchpost").click()
        assert "sec" in self.driver.page_source
        self.assertEqual(self.driver.current_url, self.get_server_url() + "/post/search")

    def test_search_post2(self):
        # search from /post/search
        self.driver.get(self.get_server_url() + "/post/search")
        self.driver.find_element_by_name("search").send_keys("sec")
        self.driver.find_element_by_name("searchpost").click()
        assert "sec" in self.driver.page_source

    def test_scan_document(self):
        # login first
        self.driver.get(self.get_server_url() + "/auth/login")
        self.driver.find_element_by_name("email").send_keys("test@gmail.com")
        self.driver.find_element_by_name("password").send_keys("testing123")
        self.driver.find_element_by_name("login").click()
        self.driver.get(self.get_server_url() + "/post/create-post")
        self.driver.execute_script("window.scrollBy(694,1366)")

        # image is located at same directory folder as selenium_test.py
        image1 = "tests/image1.png"
        with open(image1, 'rb') as f:
            r = self.Tesseract.send_ocr(f)
            assert r['response'] == True
            text_from_image = r['data']
            print(flask.url_for("post.scan_document", filename="image1.png"))
            self.driver.find_element_by_id("post-content").click();
            time.sleep(1);
            self.driver.find_element_by_id("post-content").clear()
            self.driver.find_element_by_id("post-content").send_keys(text_from_image)
        # self.driver.find_element_by_id("my-dropzone").submit()
        # self.driver.get(self.get_server_url() + "/post/scan-document")
        # self.driver.find_element_by_id("dropzoneSubmit").click()

        self.driver.find_element_by_name("post-title").send_keys("AllYourBaseBelongToUs")
        self.driver.find_element_by_name("post-description").send_keys("This is a test")
        assert "lam curious about" in self.driver.find_element_by_id("post-content").get_property('value')
        self.driver.find_element_by_name("submitpost").click()
        assert "Post has been successfully created" in self.driver.page_source


if __name__ == '__main__':
    unittest.main()
