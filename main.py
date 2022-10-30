from requests import post
from datetime import datetime, timedelta
from google.cloud import datastore
from zoneinfo import ZoneInfo

def get_post_body(current_datetime):

    epoch_today_start = current_datetime.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=ZoneInfo('GB'))
    epoch_today_end = epoch_today_start + timedelta(milliseconds=86399999)

    start = int(epoch_today_start.timestamp()) * 1000
    end = int(epoch_today_end.timestamp() * 1000)

    return {
        'aggregateBy': [
            {
                'dataTypeName': 'com.google.step_count.delta',
                'dataSourceId': 'derived:com.google.step_count.delta:com.google.android.gms:estimated_steps'
            }
        ],
        'endTimeMillis': end,
        'startTimeMillis': start
    }


def get_header():
    db = datastore.Client()

    if db == None:
        return {}

    key = db.key("fit_tokens", "fit_tokens")
    token = db.get(key)

    if token == None or 'access_token' not in token:
        return {}

    return {
        'Authorization': f"Bearer {token['access_token']}"
    }


def execute(request):
    response = post('https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate', json=get_post_body(datetime.now()),
                    headers=get_header())

    if response.status_code != 200:
        print(f'bad response from fit api endpoint: {response.status_code}')
        return { 'steps': 0 }

    step_count_delta_obj = response.json()
    steps = 0
    for step_delta in step_count_delta_obj['bucket'][0]['dataset'][0]['point']:
        steps = steps + step_delta['value'][0]['intVal']
        print(step_delta['value'][0]['intVal'], steps)

    return { 'steps': steps }