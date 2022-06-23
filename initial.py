from scan.Base import Base

import json
import requests

import base_info_scan
import service_info_scan
import policy_info_scan
import network_info_scan
import update_soft_scan
import autoruns_scan
import install_soft_scan

scan = {
    '1': base_info_scan.baseinfo_check,
    '2': install_soft_scan.inssoft_check,
    '3': network_info_scan.network_check,
    '4': update_soft_scan.update_check,
    '5': service_info_scan.service_check,
    '6': policy_info_scan.policy_check,
    '7': autoruns_scan.autorun_check
}


def user_register(value):
    jsonstr = json.dumps(value)
    print(jsonstr)
    req = requests.post('http://127.0.0.1:8082/userLines/insert',
                        headers={'Content-Type': 'application/json'},
                        data=jsonstr)
    data = req.json()  # 接收返回的json数据
    return data  # 返回字节形式


def scan_post(value, scan_id):
    # 贮存response信息
    dataList = []

    # 更新对应的扫描结果表
    url = value['url']
    send_data = value['send_data']
    # 逐个insert信息
    for data in send_data:
        # print(data)
        jsonstr = json.dumps(data, ensure_ascii=False)
        # print(jsonstr)
        req = requests.post('http://127.0.0.1:8082' + url,
                            headers={'Content-Type': 'application/json'},
                            data=jsonstr.encode('utf-8'))
        # 接收返回的json数据
        dataList.append(req.json())

    # 更新finish_time
    finish_data = {
        "id": scan_id,
        "finishTime": value['finish_time']
    }
    finish = json.dumps(finish_data)
    # print(finish)
    req = requests.post('http://127.0.0.1:8082/scan/updateById',
                        headers={'Content-Type': 'application/json'},
                        data=finish.encode('utf-8'))
    finish_res = req.json()  # 接收返回的json数据
    dataList.append(finish_res)  # 返回字节形式

    return dataList  # 返回字节形式


basename = Base.get_board_id()
# print(basename)
username = "usertest5"
# 组装发送的数据
send_data = {
    "username": username,
    "basename": basename
}

msg = user_register(send_data)
# print(msg)
data = msg['data']

if data:
    for task in data:
        # print(task)
        result = scan.get(task['scanType'])(task["id"], basename)
        # print(result)
        print(scan_post(result, task["id"]))
