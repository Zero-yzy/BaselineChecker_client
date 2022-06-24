import datetime

import vulnerable_scan
from scan.Base import Base
import json
import requests
import base_info_scan
import service_info_scan
import policy_info_scan
import network_info_scan
import update_soft_scan
import autoruns_scan
from gooey import Gooey, GooeyParser
import random
import re

scan = {
    '1': base_info_scan.baseinfo_check,
    '2': autoruns_scan.autorun_check,
    '3': network_info_scan.network_check,
    '4': update_soft_scan.update_check,
    '5': service_info_scan.service_check,
    '6': policy_info_scan.policy_check,
    '7': vulnerable_scan.vulnerable_check
}

serveIp = "127.0.0.1:8082"


def user_register(value):
    jsonstr = json.dumps(value)
    print(jsonstr)
    req = requests.post('http://' + serveIp + '/userLines/insert',
                        headers={'Content-Type': 'application/json'},
                        data=jsonstr)
    data = req.json()  # 接收返回的json数据
    return data  # 返回字节形式

#用于创建扫描任务后，插入服务端任务列表
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
        req = requests.post('http://' + serveIp + url,
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
    req = requests.post('http://' + serveIp + '/scan/updateById',
                        headers={'Content-Type': 'application/json'},
                        data=finish.encode('utf-8'))
    finish_res = req.json()  # 接收返回的json数据
    dataList.append(finish_res)  # 返回字节形式

    return dataList  # 返回字节形式

#执行轮询任务
def scan_poll(username):
    basename = Base.get_board_id()

    # 组装发送的数据
    send_data = {
        "username": username,
        "basename": basename
    }
    #发送用户名绑定，返回需要完成的任务
    msg = user_register(send_data)
    # print(msg)
    data = msg['data']
    showlist = []
    if data:
        for task in data:
            # print(task)
            result = scan.get(task['scanType'])(task["id"], basename)
            showlist.append(result)
            scan_post(result, task["id"])

    return showlist

#主动创建扫描任务并执行
def scan_create(task_type):
    # 获取主板ID
    basename = Base.get_board_id()
    # 随机赋值2开头的序号作为扫描任务序号
    task_num = 20000 + random.randint(1, 9999)
    # 扫描起始时间
    start_time = datetime.datetime.now()
    start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    # 通过发布的扫描类型，调用对应扫描函数，并向客户端发送结果
    result = scan.get(task_type)(task_num, basename)
    scan_post(result, task_num)
    # 扫描结束时间
    finish_time = datetime.datetime.now()
    finish_time = finish_time.strftime("%Y-%m-%d %H:%M:%S")
    # 扫描入表
    scan_data = {
        "id": task_num,
        "basename": basename,
        "scanType": task_type,
        "scanTime": start_time,
        "finishTime": finish_time
    }
    scan_str = json.dumps(scan_data)
    requests.post('http://' + serveIp + '/scan/insert',
                  headers={'Content-Type': 'application/json'},
                  data=scan_str.encode('utf-8'))
    # 返回结果
    return result


@Gooey(
    richtext_controls=True,  # 打开终端对颜色支持
    program_name="基线安全检测客户端",  # 程序名称
    encoding="utf-8",
    language='chinese',
    clear_before_run=True
)
def BaselineCheck():
    #加入GUI界面
    settings_msg = '此客户端程序为Windows基线安全核查设计'
    parser = GooeyParser(description=settings_msg)

    #轮询模块
    subs = parser.add_subparsers(help='commands', dest='command')
    bind = subs.add_parser('轮询执行任务', help='轮询')
    bind.add_argument("username1", metavar='用户名', help='输入用户名后执行轮询任务', widget="TextField")

    #创建任务模块
    create_task = subs.add_parser('创建扫描任务', help='用户主动发起扫描任务')
    create_task.add_argument("username2", metavar='用户名', help='请输入用户名', widget="TextField")
    create_task.add_argument("task", metavar='选择目标任务执行',
                             help='主动发起扫描任务',
                             choices=['任务1：基本信息', '任务2：自启动项', '任务3：网络信息', '任务4：补丁信息', '任务5：服务信息', '任务6：策略信息','任务7：后门信息'],
                             default='任务1：基本信息')
    args = parser.parse_args()

    if args.command == "轮询执行任务":  # 判断是执行哪个parser
        show = scan_poll(args.username1)

    if args.command == "创建扫描任务":
        str = args.task
        num = re.findall('\d', str)
        show = scan_create(num[0])

    print(show, flush=True)  # flush=True在打包的时候会用到


if __name__ == '__main__':
    BaselineCheck()
