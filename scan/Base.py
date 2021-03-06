import ctypes
import sys

import wmi
import socket
import subprocess
import psutil
import re
import platform
import json
import datetime
import winreg
import time

"""
该类用作扫描
"""


class Base:

    # 获取主板id
    @staticmethod
    def get_board_id():
        # 获取wmi对象
        c = wmi.WMI()
        # 读取主板信息
        board_info = c.Win32_BaseBoard()
        # 获取主板id
        board_id = board_info[0].SerialNumber.strip()
        return board_id

    # 获取IP
    @staticmethod
    def get_ip():
        # 获取主机名
        hostname = socket.gethostname()
        # 通过主机名获得IP
        return socket.gethostbyname(hostname)

    # 获取cmd运行结果
    @staticmethod
    def run_code(cmd):
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in res.communicate():
            return line.decode("UTF-8")

    # 获取当前设备的基本信息
    @staticmethod
    def get_base_info(scanId, basename):
        # 获取开放端口
        cmd = "netstat -ano | findstr LISTENING"
        pattern = r"[0-9]+.[0-9]+.[0-9]+.[0-9]+:(\d+)"
        result = Base.run_code(cmd)
        result = re.findall(pattern, result)
        result = list(set(result))
        result.remove("0")

        # 获取内存信息
        mem = psutil.virtual_memory()
        total_mem = round(mem.total / (1024 * 1024 * 1024), 2)
        used_mem = round(mem.used / (1024 * 1024 * 1024), 2)
        mem_use_rate = mem.percent

        # 获取注册时间
        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M:%S")

        dic_info = [{
            "scanId": scanId,
            "basename": basename,
            "hostname": platform.uname()[1],
            "ip": Base.get_ip(),
            "osInfo": platform.uname()[0] + " " + platform.uname()[2] + " v" + platform.uname()[3],
            "cpuInfo": platform.uname()[5] + " " + str(psutil.cpu_percent(0)) + "%",
            "openPort": ",".join(result),
            "usedMemory": str(used_mem) + "/" + str(total_mem) + "=" + str(mem_use_rate) + "%",
            "registerTime": time
        }]
        return dic_info

    # 扫描安装软件列表
    @staticmethod
    def get_install_soft(task_id, basename):

        # 定义注册表安装卸载软件检测位置，下列两种位置都可以找到
        # r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'
        # r'SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall'
        # r: 表示去掉转义机制
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'

        # 获取句柄handle(把注册表对象转换为python对象)
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_key, 0, winreg.KEY_ALL_ACCESS)
        # print(key)
        software_name = []
        # 通过winreg.QueryInfoKey(key)[0]获取当前注册表中的总个数
        for j in range(0, winreg.QueryInfoKey(key)[0] - 1):
            try:
                # 获取应用软件的尾缀名称(一般情况下都是软件名称，但是有特例：{69CFC76B-3434-4919-8885-BA7960725137})
                key_name = winreg.EnumKey(key, j)
                # print(key_name)
                # 组装完整的注册表软件路径
                key_path = sub_key + '\\' + key_name
                # print(key_path)
                each_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_ALL_ACCESS)
                # print(each_key)

                display_name, rgz = winreg.QueryValueEx(each_key, 'DisplayName')
                # print(rgz)
                # DisplayName = DisplayName.encode('utf-8')
                software_name.append(display_name)
            except WindowsError:
                pass

        software_name = list(set(software_name))
        software_name = sorted(software_name)
        return json.dumps(software_name)

    # 获取网络配置信息
    @staticmethod
    def get_network_info(task_id, basename):
        # 实例化wmi类
        w = wmi.WMI()
        #  配置及获取网络连接相关信息
        wmi_win32_network_adapter_configuration = w.Win32_NetworkAdapterConfiguration(IPEnabled=1)
        print(wmi_win32_network_adapter_configuration)
        json_result = json.dumps(wmi_win32_network_adapter_configuration, default=Base.network2dict)

        result = json.loads(json_result)
        print(result)

        for item in result:
            item["scanId"] = task_id
            item["basename"] = basename

        return result

    # 网络信息转dict
    @staticmethod
    def network2dict(obj):
        info = {
            "ipAddress": obj.IPAddress[0],
            "netMask": obj.IPSubnet[0],
            "mac": obj.MACAddress
        }

        return info

    # 获取自启动项列表
    @staticmethod
    def get_autoruns(task_id, basename):
        # 1. 连接注册表根键
        root1 = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        root2 = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        result = []
        try:
            # 2. 指定想要访问的子健
            reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            # 3. 打开相应子健
            key1 = winreg.OpenKey(root1, reg_path)  # 打开localmachine的autorun列表
            key2 = winreg.OpenKey(root2, reg_path)  # 打开currentuser的autorun列表
            try:
                count = 0
                while 1:
                    try:
                        # 4. 通过winreg对象的EnumValue()方法迭代其中的键值
                        n, v, t = winreg.EnumValue(key1, count)
                        result.append({
                            "scanId": task_id,
                            "basename": basename,
                            "autoName": n,
                            "autoRunner": v
                        })
                        count += 1
                    except EnvironmentError:
                        break
                count = 0
                while (1):
                    try:
                        n, v, t = winreg.EnumValue(key2, count)
                        result.append({
                            "scanId": task_id,
                            "basename": basename,
                            "autoName": n,
                            "autoRunner": v
                        })
                        count += 1
                    except EnvironmentError:
                        break
            finally:
                # 5. 关闭相应子健
                winreg.CloseKey(key1)
                winreg.CloseKey(key2)
        finally:
            # 6. 关闭相应根键连接
            winreg.CloseKey(root1)
            winreg.CloseKey(root2)
        print(result)
        return result

    # 检测补丁安装情况
    @staticmethod
    def update_information():
        # 用于获取windows更新补丁相关信息
        update_obj = wmi.WMI().Win32_QuickFixEngineering()
        list_fix = []
        for s in update_obj:
            list_fix.append([s.HotFixID, s.InstalledOn, s.Description, s.IstalledBy])
        return list_fix

    # 获得最后升级日期
    @staticmethod
    def get_last_update():
        # fix_list = []
        fix_list = Base.update_information()
        print(fix_list)
        # 获取最近更新日期
        last_day = (fix_list[0][1], time.mktime(time.strptime(fix_list[0][1], '%m/%d/%Y')))
        for fix_item in fix_list:
            # 转换为时间戳方便比较
            if fix_item[1]:
                time_stamp = time.mktime(time.strptime(fix_item[1], '%m/%d/%Y'))
                if time_stamp > last_day[1]:
                    last_day = (fix_item[1], time_stamp)
        return last_day[0]

    # 获取补丁信息
    @staticmethod
    def get_update_info(task_id, basename):
        update_obj = wmi.WMI().Win32_QuickFixEngineering()
        result = []
        for s in update_obj:
            result.append({
                "scanId": task_id,
                "basename": basename,
                "hotFixId": s.HotFixID,
                "installedOn": s.InstalledOn,
                "updateDescription": s.Description,
                "installedBy": s.InstalledBy
            })

        return result
