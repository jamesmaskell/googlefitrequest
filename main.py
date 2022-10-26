from requests import post
from datetime import datetime, timedelta
from google.cloud import datastore

def get_post_body():
    epoch_today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
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

    key = db.key("fit_tokens", "fit_tokens")
    token = db.get(key)

    return {
        'Authorization': f"Bearer {token['access_token']}"
    }


def execute(request):
    response = post('https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate', json=get_post_body(),
                    headers=get_header())
    step_count_delta_obj = response.json()

    steps = 0
    for step_delta in step_count_delta_obj['bucket'][0]['dataset'][0]['point']:
        steps = steps + step_delta['value'][0]['intVal']

    return steps