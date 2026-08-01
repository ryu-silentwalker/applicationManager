import asyncio
import json
import lib.linkedInApiManager

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
with open('test_out.json','w',encoding='utf-8') as out:
    json.dump(lib.linkedInApiManager.query(queryObj).getJobBatch(),out, indent=2)