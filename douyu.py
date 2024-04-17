import os
import json
import requests

def check_live_status(room_id):
    url = f'https://open.douyucdn.cn/api/RoomApi/room/{room_id}'
    response = requests.get(url)
    data = response.json()
    if data['error'] == 0:
        room_name = data['data']['room_name']
        owner_name = data['data']['owner_name']
        start_time = data['data']['start_time']
        return data['data']['room_status'] == '1', room_name, owner_name, start_time
    else:
        return False, None, None, None

def send_pushplus_message(token, title, content):
    url = 'http://www.pushplus.plus/send'
    data = {
        'token': token,
        'title': title,
        'content': content,
        'template': 'html'
    }
    response = requests.post(url, data=data)
    return response.json()['code'] == 200

def load_live_statuses():
    if os.path.exists(live_statuses_path):
        with open(live_statuses_path, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_live_statuses(live_statuses):
    with open(live_statuses_path, 'w') as f:
        json.dump(live_statuses, f)

if __name__ == '__main__':
    room_ids = os.environ['ROOM_IDS'].split(',')
    pushplus_token = os.environ['PUSHPLUS_TOKEN']
    live_statuses_path = os.environ['LIVE_STATUSES_PATH']

    live_statuses = load_live_statuses()
    for room_id in room_ids:
        try:
            is_live, room_name, owner_name, start_time = check_live_status(room_id)
            if is_live:
                if room_id not in live_statuses or live_statuses[room_id]['start_time'] != start_time:
                    title = f'{owner_name} 开播啦!'
                    content = f'<b>{owner_name}</b> 正在直播 <a href="https://www.douyu.com/{room_id}">《{room_name}》</a>,快去围观吧!'
                    response = send_pushplus_message(pushplus_token, title, content)
                    if response:
                        print(f'{owner_name}的开播通知已发送。')
                        live_statuses[room_id] = {'start_time': start_time}
                    else:
                        print(f'发送{owner_name}的开播通知失败。')
            else:
                if room_id in live_statuses:
                    del live_statuses[room_id]
        except Exception as e:
            print(f'检查{room_id}状态时出错:{str(e)}')
    save_live_statuses(live_statuses)
