from login import login_func
import json


session = login_func()
notification_url = 'http://myapi.afreecatv.com/api/favorite'
notify_response = session.get(notification_url)
bj_status_list = json.loads(notify_response.text)['data']

live_base_url = 'http://play.afreecatv.com/'

for bj in bj_status_list:
    if bj['is_live']:
        live_url = live_base_url + '{}/{}'.format(bj['broad_info'][0]['user_id'], bj['broad_info'][0]['broad_no'])
        print(live_url)
