from scan.Base import Base
import json
import requests
import base_info_socket
import autoruns_socket
import install_soft_socket
import network_info_socket
import policy_info_socket
import service_info_socket
import update_soft_socket

scan = {
    '1': base_info_socket.baseinfo_check,
    '2': install_soft_socket.inssoft_check,
    '3': network_info_socket.network_check,
    '4': update_soft_socket.update_check,
    '5': service_info_socket.service_check,
    '6': policy_info_socket.policy_check,
    '7': autoruns_socket.autorun_check
}
def user_register(value):
    jsonstr = json.dumps(value)
    print(jsonstr)
    req = requests.post('http://10.133.60.80:8077/userLines/insert',
                        headers = {'Content-Type':'application/json'},
                        data = jsonstr)
    data = req.json()  # 接收返回的json数据
    return data  # 返回字节形式


basename = Base.get_board_id()
print(basename)
username = "yzy"
# 组装发送的数据
send_data = {
    "username":username,
    "basename":basename}

msg = user_register(send_data)
print(msg)
data = msg['data']


if data:
    target_server_ip = '10.133.60.80'
    port = 9999
    for task in data:
        print(task)
        scan.get(task['scanType'])(target_server_ip,port,task['id'])





