import os
import re
import urllib.parse
from json import load
from time import sleep
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class linkedInBot():
    def __init__(self,resumeName,jobBlob):
        self.loginUri = "https://www.linkedin.com/login/?trk=guest_homepage-basic_nav-header-signin"
        self.driver = webdriver.Firefox()
        self.jobBlob = jobBlob
        self.resumeName = resumeName
        load_dotenv()
        self.user = os.getenv("user")
        self.passwd = os.getenv("passwd")
        self.userAA = os.getenv("userAA")

    def login(self):
        self.driver.get(self.loginUri)
        with open("cookies","r",encoding="utf-8") as cookyFile:
            cookies = load(cookyFile)
            for cookie in cookies:
                self.driver.add_cookie({"name": cookie["name"],"value": cookie["value"]})
        emailBox = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID,"«R3jvukejj35655j6»")))
        emailBox.clear()
        emailBox.send_keys(self.user)
        passwdBox = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID,"«Rlvukejj35655j6»")))
        passwdBox.clear()
        passwdBox.send_keys(self.passwd)
        loginBox = self.driver.find_element(By.XPATH, "//span[text()='Sign in']").find_element(By.XPATH,"./..").find_element(By.XPATH,"./..")
        self.driver.execute_script("arguments[0].click();", loginBox)

    def gotoJob(self,obj):
        self.driver.get(obj['link'])

    def getLinkByRegex(self,pattern):
        workday_regex_pattern = re.compile(rf'{pattern}')
        for link in self.driver.find_elements(By.TAG_NAME, "a"):
            href = link.get_attribute("href")
            if href and workday_regex_pattern.search(href):
                return link
    def addFile(self):
        self.driver.find_element(By.CSS_SELECTOR, "input[type='file']").send_keys(os.path.abspath(self.resumeName))
        self.driver.find_element(By.CLASS_NAME,"css-nay4tc").click()

    def newLoginWorkDay(self):
        try:
            userIdBox =       self.driver.find_element(By.ID,"input-4")
            passwdBox =       self.driver.find_element(By.ID,"input-5")
            verifyPasswdBox = self.driver.find_element(By.ID,"input-6")
            EULAAgree =       self.driver.find_element(By.ID,"input-9")
            createAccount =   self.driver.find_element(By.CLASS_NAME, "css-1ojdxh")
            userIdBox.clear()
            userIdBox.send_keys(self.userAA)
            passwdBox.clear()
            passwdBox.send_keys(self.passwd)
            verifyPasswdBox.clear()
            verifyPasswdBox.send_keys(self.passwd)
            EULAAgree.click()
            createAccount.click()
        except Exception as e:
            return e

    def loginWorkDay(self):
        try:
            userIdBox =       self.driver.find_element(By.ID,"input-4")
            passwdBox =       self.driver.find_element(By.ID,"input-5")
            loginBox =   self.driver.find_element(By.CLASS_NAME, "css-1ojdxh")
            userIdBox.clear()
            userIdBox.send_keys(self.userAA)
            passwdBox.clear()
            passwdBox.send_keys(self.passwd)
            loginBox.click()
        except Exception as e:
            return e

    def apply(self):
        sleep(1)
        postUrl = urllib.parse.unquote(str(self.getLinkByRegex('/safety/go').get_attribute("href"))[40:])
        self.driver.get(postUrl)
        sleep(5)
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.getLinkByRegex('workday'))).click()
        except:
            input()
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"[data-automation-id=\"autofillWithResume\"]"))).click()
        except:
            input()
        sleep(5)
        self.newLoginWorkDay()
        sleep(5)
        self.loginWorkDay()
        sleep(5)
        self.addFile()
    def autoApply(self):
        self.login()
        sleep(6)
        for el in self.jobBlob:
            self.gotoJob(self.jobBlob[el])
            self.apply()
