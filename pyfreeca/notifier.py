from login import login_func
import json
import time

session = login_func()


tmp_list = []
initial_index = 0
while True:
    notification_url = 'http://myapi.afreecatv.com/api/favorite'
    notify_response = session.get(notification_url)
    bj_status_list = json.loads(notify_response.text)['data']

    live_base_url = 'http://play.afreecatv.com/'

    onair_bj = []
    for bj in bj_status_list:
        if bj['is_live']:
            live_url = live_base_url + '{}/{}'.format(bj['broad_info'][0]['user_id'], bj['broad_info'][0]['broad_no'])
            bj_name = live_url.split('/')[-2]
            onair_bj.append(bj_name)
    print('onair: ', len(onair_bj), onair_bj)
    for i in tmp_list:
        if i in onair_bj:
            onair_bj.remove(i)
        else:
            tmp_list.remove(i)
    if len(onair_bj) != 0:
        for i in onair_bj:
            tmp_list.append(i)
    if initial_index == 0:
        tmp_list = onair_bj
    initial_index += 1
    print('tmp: ', len(tmp_list), tmp_list)
    time.sleep(10)
