#!/usr/bin/env python3

from pprint import pprint
from datetime import datetime, timedelta, timezone

import calendar
import re
import sys

from dateutil.relativedelta import relativedelta
from decouple import config

import requests

from api_client import TogglClientApi

description_pattern = config('DESCRIPTION_PATTERN', default=r'\#[a-z0-9]{5,6}(\s|$)')

settings = {
    'token': config('TOGGL_TOKEN'),
    'user_agent': config('TOGGL_USER_AGENT', default='api-agent'),
    'workspace_id': config('TOGGL_WORKSPACE_ID', default=0)  # required by TogglClientApi
}
toggl_client = TogglClientApi(settings)

print()

target_date = datetime.today()

if len(sys.argv) == 2 and sys.argv[1] == 'last':
    target_date = target_date - relativedelta(months=1)

    month = target_date.month
    year = target_date.year

else:
    month = target_date.month
    year = target_date.year

last_day = calendar.monthrange(year, month)[1]

start_date = datetime(year, month, 1, tzinfo=timezone.utc).isoformat()

end_date = datetime(year, month, last_day, tzinfo=timezone.utc) + timedelta(1) - relativedelta(seconds=1)
end_date = end_date.isoformat()

print('Start date: {}'.format(start_date))
print('End date: {}'.format(end_date))

response = toggl_client.query('/time_entries', params=dict(
    start_date=start_date,
    end_date=end_date
))


# pprint(response.json())

total_duration = 0
entries_count = 0
running_count = 0
first_entry = last_entry = None

for item in response.json():
    desc = item.get('description')
    duration = item.get('duration')
    
    # print('- duration {}s = {:.0f}h {:.0f}m'.format(
    #     duration,
    #     int(duration / 60 / 60),
    #     (duration / 60 % 60)
    # ))

    # process only stopped entries
    if 'stop' not in item:
        running_count += 1

        print('Skipped running entry starting at {}'.format(
            item.get('start')
        ))
        continue

    total_duration += duration

    if not first_entry:
        first_entry = item

    last_entry = item

    entries_count += 1

    if not desc or not bool(re.search(description_pattern, desc)):
        print()
        print('Missing pattern {} in entry description:\n'.format(
            description_pattern
        ))
        pprint(item)
        exit(1)
        break

#pprint(first_entry)
#pprint(last_entry)

if entries_count > 1000:
    raise NotImplementedError('You have more than 1000 entries')

print()
print('Entries count: {}'.format(entries_count))
print('Running entries count: {}'.format(running_count))

if first_entry:
    print()
    print('First entry: {}'.format(
        first_entry.get('start')
    ))
    print('Last entry: {}'.format(
        last_entry.get('start')
    ))

print()
print('Total duration: {:.0f}h {:.0f}m'.format(
    int(total_duration / 60 / 60),
    (total_duration / 60 % 60)
))
