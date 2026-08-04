import asyncio
import json
from time import sleep
import lib.linkedInApiManager
import lib.applicationBot

queryObj = {
        "host": "www.linkedIn.com",
        "keyword": "cyber",
        "location": "USA",
        "dateSincePosted": "24hr",
        "salary": 100000,
        "jobType": "full-time",
        "remoteFilter": "remote",
        "experienceLevel": "senior",
        "sortBy":"recent",
        "limit":10,
        "page":1,
        "verification": True,
        "under10": True
}

obj = {
        "job": {
                "title": "Cyber - Palo Alto SecOps - Senior Consultant",
                "location": "Boston, MA",
                "postedTime": "2026-08-01",
                "link": "https://www.linkedin.com/jobs/view/security-architect-at-thyssenkrupp-4447976863/?refId=8If7aQDyUCPF68PSEWK2Vg%3D%3D&trackingId=m4bD9uYlK6emWSAdWahpDQ%3D%3D"
}}
#with open('test_out.json','w',encoding='utf-8') as out:
#    json.dump(lib.linkedInApiManager.query(queryObj).getJobBatch(),out, indent=2)


#bot = lib.applicationBot.linkedInBot(lib.linkedInApiManager.query(queryObj).getJobBatch())
bot = lib.applicationBot.linkedInBot("./resume/Ryu_Silentwalker_Resume.docx",obj)
bot.autoApply()