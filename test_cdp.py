# test_qq_full.py - 获取 QQ 账号、好友/群名

import time
import win32gui
import win32process
import psutil
import keyboard
import uiautomation as auto

QQ_CLASS = "Chrome_WidgetWin_1"

def get_window_pid(hwnd):
    """获取窗口所属进程 ID"""
    tid, pid = win32process.GetWindowThreadProcessId(hwnd)
    return pid

def get_process_name(pid):
    """获取进程名"""
    try:
        return psutil.Process(pid).name()
    except:
        return None

def get_qq_windows():
    """获取所有 QQ 相关窗口，按进程分组"""
    qq_windows = []
    
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            class_name = win32gui.GetClassName(hwnd)
            title = win32gui.GetWindowText(hwnd)
            
            if class_name == QQ_CLASS:
                pid = get_window_pid(hwnd)
                proc_name = get_process_name(pid)
                
                # 只保留 QQ 进程
                if proc_name and "QQ" in proc_name:
                    qq_windows.append({
                        'hwnd': hwnd,
                        'title': title,
                        'pid': pid,
                        'is_main': title == "QQ",  # 效率模式主窗口
                    })
        return True
    
    win32gui.EnumWindows(callback, None)
    return qq_windows

def analyze_qq_windows(windows):
    """分析窗口关系"""
    # 按 PID 分组（每个 PID 是一个 QQ 账号）
    by_pid = {}
    for w in windows:
        pid = w['pid']
        if pid not in by_pid:
            by_pid[pid] = []
        by_pid[pid].append(w)
    
    print(f"发现 {len(by_pid)} 个 QQ 账号：\n")
    
    for pid, wins in by_pid.items():
        print(f"账号 PID: {pid}")
        
        # 找主窗口
        main = [w for w in wins if w['is_main']]
        chats = [w for w in wins if not w['is_main']]
        
        if main:
            print(f"  [主窗口] QQ")
        
        print(f"  [聊天窗口] {len(chats)} 个：")
        for chat in chats:
            print(f"    - {chat['title']}")
        
        print()

def test():
    windows = get_qq_windows()
    print(windows)

    if len(windows)==0: 
        keyboard.send('win+m')
        time.sleep(0.5)
        for i in range(5):
            time.sleep(0.1)
            keyboard.send('tab')
        for i in range(2):
            time.sleep(0.1)
            keyboard.send('right')
        keyboard.send('enter')
        time.sleep(0.5)
    
    windows = get_qq_windows()
    # print(windows)
    
    for w in windows:
        # print(w)
        # for key in w:
        #     print(f"{key}: {w[key]}")
        print(w["hwnd"])
        w["uia_windows"] = auto.ControlFromHandle(w["hwnd"])
        print(w["uia_windows"])

        def traverse_qq_controls_compatible(control, depth=0):
            """兼容版遍历：穿透六层嵌套面板，打印核心信息（无缺失属性也能运行）"""
            indent = "  " * depth
            # 基础信息（只取肯定存在的属性）
            ctrl_name = getattr(control, "Name", "无")
            ctrl_type = getattr(control, "ControlType", "未知")
            ctrl_enabled = getattr(control, "IsEnabled", "未知")
            
            # 打印信息（重点标注非PaneControl的控件）
            type_cn = "面板(Pane)" if ctrl_type == 50033 else f"其他({ctrl_type})"
            print(f"{indent}层级{depth} | 名称：{ctrl_name} | 类型：{type_cn} | 可用：{ctrl_enabled}")

            # 递归遍历子控件（穿透六层嵌套）
            try:
                children = control.GetChildren()
                for child in children:
                    traverse_qq_controls_compatible(child, depth + 1)
            except Exception as e:
                # 遇到无GetChildren的控件，跳过（避免崩溃）
                print(f"{indent}⚠️ 层级{depth}控件无子控件：{e}")
        
        # 执行遍历，打印所有组件特征（运行后查看输出，找到目标组件的特征）
        print("=== QQ根面板下所有组件特征（层级展示）===")
        traverse_qq_controls_compatible(w["uia_windows"])
        item = w["uia_windows"].GetChildren()[1] # 层 1
        item = item.GetChildren()[0]             # 层 2
        item = item.GetChildren()[0]             # 层 3
        item = item.GetChildren()[0]             # 层 4
        item = item.GetChildren()[0]             # 层 5
        item = item.GetChildren()                # 层 6
        for i in item:
            print(i)
            i.SetActive()

        # items = w["uia_windows"].GetChildren()
        # for item in items:
        #     # print(item)
        #     c_items = item.GetChildren()
        #     if len(c_items) == 0:
        #         continue
        #     print(c_items)
        #     print(len(c_items))
        #     # print(c_items[0])
        #     print(c_items[0].GetChildren())
        w["uia_windows"].SetActive()
        focused_ctrl = None
        for i in range(1,11):
            focused_ctrl = auto.GetFocusedControl()
            if not focused_ctrl:
                print(f"第{i}个控件不存在/未聚焦")
                continue
            print(f"\n 第{i}个控件为{focused_ctrl.Name}")
            print(focused_ctrl)
            traverse_qq_controls_compatible(focused_ctrl)
            # if "的头像" in focused_ctrl.Name:
            #     # print(focused_ctrl)

            time.sleep(0.1)
            keyboard.send('tab')

    analyze_qq_windows(windows)

if __name__ == "__main__":
    test()