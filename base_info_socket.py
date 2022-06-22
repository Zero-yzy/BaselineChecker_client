import socket
import datetime
from const.Type import Type
from scan.Base import Base

def baseinfo_check(target_server_ip, port, task_id):
    # 准备ip和端口
    address = (target_server_ip, port)
    # 创建socket对象
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 连接
    client_socket.connect(address)
    print('连接服务端成功')
    # 获取主板id
    board_id = Base.get_board_id()
    # 获取基本信息
    data = Base.get_base_info()
    # data的双引号转换为单引号
    data = data.replace('"', "'")
    # 组装发送的类型
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    send_data = '{"typeCode":%d,"basename":"%s","finish_time":"%s","scanid":"%s","data":"%s"}' % (Type.BASE_INFO, board_id, time, task_id, data)
    # print(send_data)
    # 发送
    client_socket.send(send_data.encode('utf-8'))
    print('发送成功')

    # 关闭
    client_socket.close()


