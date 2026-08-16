import re
import time
import requests
import urllib.parse
from json import load
from random import random
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

class bypassBotDetect:
    def __init__(self,jobBlobUnfiltered):
        options=Options()
        options.add_argument("--headless=new")
        self.driver = webdriver.Firefox(options=options)
        self.jobBlobUnfiltered = jobBlobUnfiltered

    def close(self):
        """Cleans up the WebDriver session."""
        print("Job application loop complete. Closing browser...")
        try:
            self.driver.quit()
        except Exception as e:
            print(f"Error closing browser: {e}")
    def login(self):
        self.driver.get("https://www.linkedin.com/login")
        time.sleep(2)

        # 1. Inject Cookies
        try:
            with open("cookies.json", "r", encoding="utf-8") as cookyFile:
                cookies = load(cookyFile)
                for cookie in cookies:
                    self.driver.add_cookie({"name": cookie["name"], "value": cookie["value"]})

            # Refresh to apply cookies
            self.driver.refresh()
            time.sleep(3)
        except Exception as e:
            print(f"Cookie injection skipped: {e}")

        # 2. Check if cookies successfully logged us in (Redirected to feed)
        if "feed" in self.driver.current_url:
            print("Successfully logged in via cookies!")
            return

        # 3. Wait for LinkedIn's actual username/email selector
        try:
            emailBox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "username"))
            )
            passwdBox = self.driver.find_element(By.ID, "password")

            emailBox.clear()
            emailBox.send_keys(self.user)
            passwdBox.clear()
            passwdBox.send_keys(self.passwd)

            # LinkedIn submit button
            loginBtn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            loginBtn.click()

        except Exception:
            # If it times out, check if LinkedIn triggered a CAPTCHA/Verification checkpoint
            if "checkpoint" in self.driver.current_url:
                print("LinkedIn triggered a Security Checkpoint / CAPTCHA verification.")
            else:
                print("Failed to locate login fields.")
    def getLinkByRegex(self,pattern):
        regexPattern = re.compile(rf'{pattern}')
        for link in self.driver.find_elements(By.TAG_NAME, "a"):
            href = link.get_attribute("href")
            if href and regexPattern.search(href):
                return link
    def getReversedLink(self):
            tty = 0
            try:
                while tty < 10:
                    try:
                        raw_href = self.getLinkByRegex('/safety/go').get_attribute("href")
                        post_url = urllib.parse.unquote(str(raw_href)[40:])
                        if post_url != None: return post_url
                    except:
                        time.sleep(3)
                        tty += 1
            except Exception:
                return None
    def processBlob(self):
        filteredBlob = dict()
        self.login()
        for el in self.jobBlobUnfiltered:
            self.driver.get(self.jobBlobUnfiltered[el]['link'])
            postProcessUrl = self.getReversedLink()
            postProcessEl = self.jobBlobUnfiltered[el].copy()
            postProcessEl.pop("link")
            postProcessEl['link'] = postProcessUrl
            filteredBlob[el] = postProcessEl.copy()
            print(f'{el} processed....')
        return filteredBlob





class query():
    def __init__(self,queryObj):
        self.host = queryObj["host"]
        self.keyword = queryObj["keyword"].strip().replace("\\s+/g", "+")
        self.location = queryObj["location"].strip().replace("\\s+/g", "+")
        self.dateSincePosted = str(queryObj["dateSincePosted"])
        self.salary = int(queryObj["salary"])
        self.jobType = str(queryObj["jobType"])
        self.remoteFilter = str(queryObj["remoteFilter"])
        self.experienceLevel = str(queryObj["experienceLevel"])
        self.sortBy = queryObj["sortBy"]
        self.limit = int(queryObj["limit"])
        self.page = int(queryObj["page"])
        self.verification = bool(queryObj["verification"])
        self.under10 = bool(queryObj["under10"])

    def getDateSincePosted(self):
        dateRange = {
            "past month": "r2592000",
            "past week": "r604800",
            "24hr": "r86400",
        }
        if self.dateSincePosted == None or self.dateSincePosted == "":
            return ""
        return dateRange[self.dateSincePosted.lower()]
    def getExperienceLevel(self):
        experienceRange = {
            "internship": "1",
            "entry level": "2",
            "associate": "3",
            "senior": "4",
            "director": "5",
            "executive": "6",
        }
        if self.experienceLevel == None or self.experienceLevel == "":
                    return ""
        return experienceRange[self.experienceLevel.lower()]
    def getJobType(self):
        jobTypeRange = {
            "full time": "F",
            "full-time": "F",
            "part time": "P",
            "part-time": "P",
            "contract": "C",
            "temporary": "T",
            "volunteer": "V",
            "internship": "I",
        }
        if self.jobType == None or self.jobType == "":
                    return ""
        return jobTypeRange[self.jobType.lower()]
    def getRemoteFilter(self):
        remoteFilterRange = {
          "on-site": "1",
          "on site": "1",
          "remote": "2",
          "hybrid": "3",
        }
        return remoteFilterRange[self.remoteFilter.lower()]
    def getSalary(self):
        match self.salary:
            case x if 0 < x < 60000:
                return 1
            case x if 60000 <= x < 80000:
                return 2
            case x if 80000 <= x < 100000:
                return 3
            case x if 100000 <= x < 120000:
                return 4
            case x if 120000 < x:
                return 5
            case _:
                return ""
                  
    def getSort(self):
        sortRange = {
            "recent": "DD",
            "relevant": "R"
        }
        if self.sortBy == None or self.sortBy == "":
                    return ""
        return sortRange[self.sortBy.lower()]
    def params(self,start):
        paramsFiltered = dict()
        params = {
            "keywords": str(self.keyword),
            "location": str(self.location),
            "f_TPR": str(self.getDateSincePosted()),
            "f_SB2": str(self.getSalary()),
            "f_E": str(self.getExperienceLevel()),
            "f_WT": str(self.getRemoteFilter()),
            "f_JT": str(self.getJobType()),
            "f_VJ": str(self.verification),
            "f_EA": str(self.under10),
            "start": str(start),
            "sortBy": str(self.getSort())
        }
        for param in params:
             if params[param] != None and params[param] != "":
                  paramsFiltered[param] = params[param]
        return paramsFiltered
    def getJobBlock(self,start):
        targetUri = f'https://{self.host}/jobs-guest/jobs/api/seeMoreJobPostings/search?'
        headers = {
            "User-Agent": UserAgent().random,
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.linkedin.com/jobs",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
        try:
            response = requests.get(targetUri,headers=headers,params=self.params(start),timeout=10000)
            ttl = 0
            while response.text == '<!DOCTYPE html>\n\n<!---->  ' or response.status_code!=200:
                if ttl >= 10:
                    return RuntimeError
                ttl += 1
                time.sleep(random()*10)
                response = requests.get(targetUri,headers=headers,params=self.params(start),timeout=10000)
            tastySoup = BeautifulSoup(response.text, "html.parser")
            jobBlock = dict()
            for li in tastySoup.find_all('li'):
                try :
                    title = li.find('h3',class_="base-search-card__title").contents[0].strip()
                    try: link = li.find('a',class_="base-card__full-link").get('href') 
                    except: link = None
                    location = li.find('span',class_="job-search-card__location").contents[0].strip()
                    try: postedTime = li.find('time',class_="job-search-card__listdate--new").get('datetime')
                    except: postedTime = li.find('time',class_="job-search-card__listdate").get('datetime')
                    posId = re.findall(r'\d{8,11}',link)[0]
                    jobBlock[posId] = {"title": title, "location": location, "postedTime": postedTime, "link": link}
                except Exception as e:
                    pass
            return jobBlock
        except Exception as e:
            pass

        
    def getJobBatch(self):
        block = 10
        jobBatch = dict()
        start = ((self.page*2)*25)
        while len(jobBatch) <= self.limit:
            jobBlock = self.getJobBlock(start)
            if jobBlock == RuntimeError:
                return jobBatch
            for el in jobBlock:
                jobBatch[el] = jobBlock[el]
                start = start+block
        return jobBatch


    