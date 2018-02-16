#!/usr/bin/env python
# Kyle Fitzsimmons, 2018
import dataset
from faker import Factory
import os
import sys


fake = Factory.create()


postgres_uri = os.getenv('IT_POSTGRES_URI').strip()
if not postgres_uri:
    print('IT_POSTGRES_URI env variable not found.')
    sys.exit()

db = dataset.connect(postgres_uri)


# add unique prompt_uuid for each distinct answered prompt timetstamp
# - keep track of mobile_id, timestamp, prompt_uuid to add to the cancelled prompts which share the same timestamp
all_mobile_ids = [user['id'] for user in db['mobile_users']]

stats = {
    'total_users': len(all_mobile_ids),
    'answered_prompts_edited': 0,
    'cancelled_prompts_deleted': 0,
    'cancelled_prompts_edited': 0
}
db.begin()
for mobile_idx, mobile_id in enumerate(all_mobile_ids, start=1):
    if mobile_idx % 10 == 0:
        print(mobile_idx, '/', len(all_mobile_ids))

    user_prompts = {}
    for answered_prompt in db['mobile_prompt_responses'].find(mobile_id=mobile_id, order_by='id'):
        group = user_prompts.setdefault(answered_prompt['displayed_at'], {
            'group_uuid': fake.uuid4(),
            'prompts': []
        })
        group['prompts'].append(answered_prompt)


    for timestamp, prompt_group in user_prompts.items():
        for prompt_idx, prompt in enumerate(prompt_group['prompts'], start=1):
            prompt['prompt_uuid'] = prompt_group['group_uuid']
            prompt['prompt_num'] = prompt_idx
            prompt['edited_at'] = prompt['recorded_at']
            db['mobile_prompt_responses'].upsert(prompt, ['id'])
            stats['answered_prompts_edited'] += 1

    for cancelled_prompt in db['mobile_cancelled_prompt_responses'].find(mobile_id=mobile_id):
        cancelled_timestamp = cancelled_prompt['displayed_at']
        if cancelled_timestamp in user_prompts:
            db['mobile_cancelled_prompt_responses'].delete(id=cancelled_prompt['id'])
            stats['cancelled_prompts_deleted'] += 1
        else:
            cancelled_prompt['prompt_uuid'] = fake.uuid4()
            db['mobile_cancelled_prompt_responses'].upsert(cancelled_prompt, ['id'])
            stats['cancelled_prompts_edited'] += 1
db.commit()

# ensure table have no null values
from pprint import pprint
pprint(stats)
