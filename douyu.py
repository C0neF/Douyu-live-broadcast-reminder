import requests
import time
import os

# 从环境变量获取主播的房间ID列表
room_ids = os.getenv('ROOM_IDS').split(',') if os.getenv('ROOM_IDS') else []
# 从环境变量获取pushplus的token
pushplus_token = os.getenv('PUSHPLUS_TOKEN')

def check_live_status(room_id):
    """
    检查斗鱼主播的开播状态
    """
    url = f'https://open.douyucdn.cn/api/RoomApi/room/{room_id}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get('error') == 0 and data['data'].get('room_status') == "1":
            return True, data['data'].get('room_name'), data['data'].get('owner_name')
    except requests.RequestException as e:
        print(f'请求错误: {e}')
    except KeyError as e:
        print(f'JSON格式错误: {e}')
    return False, None, None

def send_pushplus_message(token, title, content):
    """
    使用pushplus发送微信消息
    """
    url = 'https://www.pushplus.plus/send'
    data = {
        "token": token,
        "title": title,
        "content": content
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f'请求错误: {e}')
        return None

def main():
    live_statuses = {room_id: False for room_id in room_ids}  # 记录每个主播的开播状态
    while True:
        for room_id in room_ids:
            is_live, room_name, owner_name = check_live_status(room_id)
            live_status = '已开播' if is_live else '未开播'
            print(f'{owner_name} ({room_id}): {live_status}')
            if is_live and not live_statuses[room_id]:
                # 如果主播开播，并且之前的状态是未开播，则发送通知
                title = f'{owner_name} 开播啦！'
                content = f'快来看看{owner_name}的直播间：{room_name}！'
                response = send_pushplus_message(pushplus_token, title, content)
                if response:
                    print(f'{owner_name}的开播通知已发送。')
                else:
                    print(f'发送{owner_name}的开播通知失败。')
                live_statuses[room_id] = True  # 更新主播的开播状态
            elif not is_live:
                live_statuses[room_id] = False  # 如果主播未开播，重置状态
        time.sleep(60)  # 每60秒检查一次

if __name__ == '__main__':
    main()
