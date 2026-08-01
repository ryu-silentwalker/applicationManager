import os
from time import sleep
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class linkedInBot():
    def __init__(self,jobBlob):
        self.loginUri = "https://www.linkedin.com/login/?trk=guest_homepage-basic_nav-header-signin"
        self.driver = webdriver.Firefox()
        self.jobBlob = jobBlob
        load_dotenv()
        self.user = os.getenv("user")
        self.passwd = os.getenv("passwd")

    def login(self):
        self.driver.get(self.loginUri)
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

    def apply(self):
        applyButton = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID,"link-external-medium"))).find_element(By.XPATH,"./..")
        applyButton.click()
        sleep(5)
        try:
            WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*=*myworkday*]"))).click()
        except:
            pass
        try:
            WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*=*autofillWithResume*]"))).click()
        except:
            pass

    def autoApply(self):
        self.login()
        sleep(5)
        for el in self.jobBlob:
            self.gotoJob(self.jobBlob[el])
            self.apply()
