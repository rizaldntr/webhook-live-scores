import datetime
import requests
import json
from apscheduler.schedulers.blocking import BlockingScheduler
sched = BlockingScheduler()

CURRENT_URL = "https://world-cup-json.herokuapp.com/matches/current"
LIVE_BLOG_URL = "https://livebloggingdistributionapi.fifa.com/api/v1/blogs/{}/events?since={}Z"
LIST_ALL_BLOGS_URL = "https://livebloggingdistributionapi.fifa.com/api/v1/FIFA%20FORGE/en-GB/blogs?tag.IdSeason=254645&$limit=64"
AUTH_KEY = "LiveBlogging key=1FBA2B07-6619-4BF3-9DE7-F93FFBDE076C"
headers = {'authorization': AUTH_KEY}
WEBHOOK_URL = "https://wc-flask.herokuapp.com/webhook"

# Get id blog
blog_ids = []

def post_to_webhook(message):
    requests.post(WEBHOOK_URL, json={"message": message})

def update_id_blog():
    global blog_ids
    r = requests.get(CURRENT_URL)
    datas = json.loads(r.content)

    r = requests.get(LIST_ALL_BLOGS_URL, headers=headers)
    items = json.loads(r.content)['items']

    if len(datas) == 0:
        blog_ids = []
        return
    
    fifa_id = []
    for data in datas:
        fifa_id.append(data['fifa_id'])
    
    index = 0
    for item in items:
        if fifa_id[index] in item['title']:
            blog_ids.append(item['id'])
            index += 1
        
        if index == len(fifa_id):
            return

next_events = []
messages = []
def webhook_helper():
    global next_events
    global blog_ids
    global messages
    times = []
    if len(next_events) == 0:
        times = [ datetime.datetime.utcnow().isoformat() for i in range(len(blog_ids))]
        messages = ["" for i in range(len(blog_ids))]
        for idx, time in enumerate(times):
            URL = LIVE_BLOG_URL.format(blog_ids[idx], time)
            next_events.append(URL)

    for idx, event in enumerate(next_events):
        r = requests.get(event, headers=headers)
        next_events[idx] = json.loads(r.content)['meta']['nextEvents']
        items = json.loads(r.content)['items']

        for item in items:
            parts = item['body']['parts']

            for part in parts:
                if part['datasource'] == "LivePosts":
                    if messages[idx] != part['data']['Text'][3:-5]:
                        post_to_webhook(part['data']['Text'][3:-5])
                        print (part['data']['Text'][3:-5])
                        messages[idx] = part['data']['Text'][3:-5]
                elif part['datasource'] == "MatchEvents":
                    if messages[idx] != part['data']['TranslatedEventName']:
                        post_to_webhook(part['data']['TranslatedEventName'])
                        print (part['data']['TranslatedEventName'])
                        messages[idx] = part['data']['TranslatedEventName']

update_id_blog()
sched.add_job(update_id_blog, 'interval', hours=1)
sched.add_job(webhook_helper, 'interval', seconds=5)
sched.start()
