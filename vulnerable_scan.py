import winreg
import ctypes
import sys
import datetime


# 获取管理员权限
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


class Vulnerable():

    # 1. 查找是否存在影子账户
    @staticmethod
    def shadowaccount_check():

        root = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        account = {}
        valueList = []
        if is_admin():
            try:
                # 查看注册表中的账户
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SAM\SAM\Domains\Account\Users")
                try:
                    count = 0
                    while (1):
                        try:
                            # 查看全部账户并保存在account中
                            f = winreg.EnumKey(key, count)
                            account[count] = f
                            count += 1
                        except EnvironmentError:
                            break
                finally:
                    winreg.CloseKey(key)

                for i in range(len(account) - 1):
                    reg_path = r"SAM\\SAM\\Domains\\Account\\Users" + "\\" + account[i]
                    key = winreg.OpenKey(root, reg_path)
                    try:
                        count = 0
                        while (1):
                            try:
                                regKey, regValue, regType = winreg.EnumValue(key, count)
                                # 查看账户的'F'键值并保存在valuelist中
                                if regKey == 'F':
                                    valueList.append(regValue)
                                    break
                                count += 1
                            except EnvironmentError:
                                break
                    finally:
                        winreg.CloseKey(key)
            finally:
                winreg.CloseKey(root)

        else:
            if sys.version_info[0] == 3:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

        #将valuelist去重
        new_valueList = list(set(valueList))
        # 比较是否存在重复键值，存在则说明存在影子账户
        if len(new_valueList) == len(valueList):
            result = "not found"
        else:
            result = "exist"
        return result

    # 2. 查找映像劫持
    @staticmethod
    def imagehijack_check():
        root = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        try:
            #打开注册表项
            reg_path = r"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options"
            key = winreg.OpenKey(root, reg_path)
            results = {}
            HijackList = []
            try:
                count = 0
                while (1):
                    try:
                        #将映像文件项存到results中
                        f = winreg.EnumKey(key, count)
                        results[count] = f
                        count += 1
                    except EnvironmentError:
                        break
            finally:
                winreg.CloseKey(key)

            for i in range(len(results)):
                reg_path = r"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options" + "\\" + \
                           results[i]
                try:
                    key = winreg.OpenKey(root, reg_path)
                except EnvironmentError:
                    continue
                try:
                    count = 0
                    while (1):
                        try:
                            # 查看键值里是否有Debugger
                            regKey, regValue, regType = winreg.EnumValue(key, count)
                            if regKey == 'Debugger':
                                HijackList.append(results[i])
                            count += 1
                        except EnvironmentError:
                            break
                finally:
                    winreg.CloseKey(key)
        finally:
            winreg.CloseKey(root)


        return HijackList

    @staticmethod
    def get_vulnerable_info(task_id, basename):
        vulnerable_info=[]
        shadow = Vulnerable.shadowaccount_check()
        image = Vulnerable.imagehijack_check()
        if len(image) == 0:
            image.append('not found')
        for i in range(len(image)):
            vulnerable_info.append({
                "scanId": task_id,
                "basename": basename,
                "shadowResult": shadow,
                "imageResult": image[i]
            })
        return vulnerable_info

def vulnerable_check(task_id, basename):
    result = {}
    # 编辑URL
    result["url"] = "/vulnerableChecks/insert"
    # 获取基本信息
    data = Vulnerable.get_vulnerable_info(task_id, basename)
    # 组装发送的类型
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    result['finish_time'] = time
    result['send_data'] = data

    return result


