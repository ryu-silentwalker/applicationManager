import re
import json
import asyncio
import requests
from time import sleep
from random import random
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

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
            case x if x < 60000:
                return 1
            case x if 60000 <= x < 80000:
                return 2
            case x if 80000 <= x < 100000:
                return 3
            case x if 100000 <= x < 120000:
                return 4
            case x if 120000 < x:
                return 5
    def getSort(self):
        sortRange = {
            "recent": "DD",
            "relevant": "R"
        }
        return sortRange[self.sortBy.lower()]
    def params(self,start):
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
        return params
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
                sleep(random()*10)
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


    