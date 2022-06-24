import datetime
from scan.service_check import get_service_info


def service_check(task_id, basename):
    result = {}
    # 编辑URL
    result["url"] = "/serviceChecks/insert"
    # 获取基本信息
    data = get_service_info(task_id, basename)
    # 组装发送的类型
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    result['finish_time'] = time
    result['send_data'] = data
    # print(send_data.encode('utf-8'))

    return result
