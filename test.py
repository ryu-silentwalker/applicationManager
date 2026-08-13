import asyncio
import json
from time import sleep
import lib.linkedInApiManager
import lib.applicationBot

queryObj = {
        "host": "www.linkedIn.com",
        "keyword": "cyber, NetDevOps, DevSecOps, network, it",
        "location": "USA",
        "dateSincePosted": "24hr",
        "salary": 0,
        "jobType": "full-time",
        "remoteFilter": "remote",
        "experienceLevel": "",
        "sortBy":"recent",
        "limit":1000,
        "page":0,
        "verification": True,
        "under10": True
}

obj = {  "4448583771": {
    "title": "US Tech - FTO Senior Associate",
    "location": "Tulsa, OK",
    "postedTime": "2026-08-05",
    "link": "https://www.linkedin.com/jobs/view/us-tech-fto-senior-associate-at-pwc-4448583771/?refId=dPOxQvGD7s1SFkG%2BVvSvjg%3D%3D&trackingId=cQFOmqtjyA6YUK80na2HQQ%3D%3D"
  }}

#with open('test_out.json','w',encoding='utf-8') as out:
#    json.dump(lib.linkedInApiManager.query(queryObj).getJobBatch(),out, indent=2)
jobBlob= lib.linkedInApiManager.query(queryObj).getJobBatch()
with open('jobDump.json','w',encoding='utf-8') as jobDumpFile:
    json.dump(jobBlob,jobDumpFile,indent=2)