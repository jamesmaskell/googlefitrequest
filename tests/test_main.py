import datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo
import main

class TestMain(TestCase):

    def test_google_fit_request_body_created_with_correct_timestamps(self):
        expected = {
            'aggregateBy': [
                {
                    'dataTypeName': 'com.google.step_count.delta',
                    'dataSourceId': 'derived:com.google.step_count.delta:com.google.android.gms:estimated_steps'
                }
            ],
            'endTimeMillis': 1666997999999,
            'startTimeMillis': 1666911600000
        }

        result = main.get_post_body(datetime.datetime(2022, 10, 28, 1, 0, 0, 0, tzinfo=ZoneInfo('GB')))

        assert result == expected

    @patch('main.datastore.Client', MagicMock(return_value=MagicMock(get=MagicMock(return_value={'access_token': '343253645'}))))
    def test_header_is_returned_with_token(self,):
        expected = {
            'Authorization': 'Bearer 343253645'
        }

        result = main.get_header()

        assert result == expected

    @patch('main.datastore.Client', MagicMock(return_value=None))
    def test_empty_headers_returned_when_datastore_client_not_initialised(self):
        expected = {}

        result = main.get_header()

        assert result == expected

    @patch('main.datastore.Client', MagicMock(return_value=MagicMock(get=MagicMock(return_value={'token': '343253645'}))))
    def test_empty_headers_returned_when_datastore_object_does_not_contain_access_token(self):
        expected = {}

        result = main.get_header()

        assert result == expected

    @patch('main.datastore.Client', MagicMock(return_value=MagicMock(get=MagicMock(return_value=None))))
    def test_empty_headers_returned_when_datastore_object_is_none(self):
        expected = {}

        result = main.get_header()

        assert result == expected

    @patch('main.get_header', MagicMock(return_value={}))
    @patch('main.get_post_body', MagicMock(return_value={}))
    @patch('main.post', MagicMock(return_value=MagicMock(status_code=200, json=MagicMock(return_value={'bucket': [{'dataset': [{'point': [{'value': [{'intVal': 25}]}, {'value': [{'intVal': 30}]}]}]}]}))))
    def test_execute_returns_steps_value_from_fit_api(self):

        expected = { 'steps': 55 }

        result = main.execute(None)

        assert result == expected

    @patch('main.get_header', MagicMock(return_value={}))
    @patch('main.get_post_body', MagicMock(return_value={}))
    @patch('main.post', MagicMock(return_value=MagicMock(status_code=401)))
    def test_execute_returns_zero_steps_when_no_response_from_api(self):
        expected = {'steps': 0}

        result = main.execute(None)

        assert result == expected



