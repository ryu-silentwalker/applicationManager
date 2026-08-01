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
        "limit":1000,
        "page":1,
        "verification": True,
        "under10": True
}

obj = {
  "title": "Cyber - Palo Alto SecOps - Senior Consultant",
  "location": "Boston, MA",
  "postedTime": "2026-08-01",
  "link": "https://www.linkedin.com/jobs/view/cyber-palo-alto-secops-senior-consultant-at-deloitte-4447779096?position=10&pageNum=95&refId=NKk%2BCGdbKOJhaJlIJQQhrw%3D%3D&trackingId=RpYAUYG3Vfx55bhX%2BGG5zQ%3D%3D"
}
#with open('test_out.json','w',encoding='utf-8') as out:
#    json.dump(lib.linkedInApiManager.query(queryObj).getJobBatch(),out, indent=2)


bot = lib.applicationBot.linkedInBot(lib.linkedInApiManager.query(queryObj).getJobBatch())
bot.autoApply()