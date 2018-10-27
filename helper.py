import datetime
import requests
import json
import config
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.combining import AndTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

CONFIG = config.ProductionConfig

sched = BlockingScheduler()
headers = {'authorization': CONFIG.AUTH_KEY}

# Get id blog
blog_ids = []

def post_to_webhook(message):
    requests.post(CONFIG.WEBHOOK_URL, json={"message": message})

def update_id_blog():
    global blog_ids
    r = requests.get(CONFIG.CURRENT_URL)
    datas = json.loads(r.content)

    r = requests.get(CONFIG.LIST_ALL_BLOGS_URL, headers=headers)
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
    print("running webhook")
    global next_events
    global blog_ids
    global messages
    times = []
    if len(next_events) == 0:
        times = [ datetime.datetime.utcnow().isoformat() for i in range(len(blog_ids))]
        messages = ["" for i in range(len(blog_ids))]
        for idx, time in enumerate(times):
            URL = CONFIG.LIVE_BLOG_URL.format(blog_ids[idx], time)
            next_events.append(URL)

    for idx, event in enumerate(next_events):
        r = requests.get(event, headers=headers)
        next_events[idx] = json.loads(r.content)['meta']['nextEvents']
        items = json.loads(r.content)['items']

        for item in items:
            parts = item['body']['parts']

            for part in parts:
                # if part['datasource'] == "LivePosts":
                #     if messages[idx] != part['data']['Text'][3:-5]:
                #         post_to_webhook(part['data']['Text'][3:-5])
                #         print (part['data']['Text'][3:-5])
                #         messages[idx] = part['data']['Text'][3:-5]
                if part['datasource'] == "MatchEvents":
                    if messages[idx] != part['data']['TranslatedEventName']:
                        post_to_webhook(part['data']['TranslatedEventName'])
                        print (part['data']['TranslatedEventName'])
                        messages[idx] = part['data']['TranslatedEventName']

update_id_blog()
sched.add_job(update_id_blog, 'interval', minutes=3)
sched.add_job(webhook_helper, 'interval', seconds=30)
sched.start()
