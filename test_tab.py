import time
import keyboard
import win32gui
import win32process
import ctypes
from ctypes import wintypes
from pywinauto import Desktop
from pywinauto.uia_defines import IUIA

class GUIThreadInfo(ctypes.Structure):
    # 严格按照 Windows API 的格式定义字段，一个都不能错
    _fields_ = [
        ("cbSize", wintypes.DWORD),          # 结构体大小（必填）
        ("flags", wintypes.DWORD),           # 状态标志
        ("hwndActive", wintypes.HWND),       # 活动窗口句柄
        ("hwndFocus", wintypes.HWND),        # 聚焦控件句柄（你最需要的）
        ("hwndCapture", wintypes.HWND),      # 捕获鼠标的窗口
        ("hwndMenuOwner", wintypes.HWND),    # 菜单所属窗口
        ("hwndMoveSize", wintypes.HWND),     # 正在拖动的窗口
        ("hwndCaret", wintypes.HWND),        # 光标所在窗口
        ("rcCaret", wintypes.RECT)           # 光标位置矩形
    ]

def get_tooltip_text():
    """获取当前显示的悬浮提示（Tooltip）文本"""
    tooltip_text = ""
    # 存储所有Tooltip窗口句柄（类名：tooltips_class32）
    tooltip_hwnds = []

    # 回调函数：遍历所有窗口，筛选Tooltip窗口
    def enum_tooltip_callback(hwnd, hwnd_list):
        if win32gui.GetClassName(hwnd) == "tooltips_class32":
            hwnd_list.append(hwnd)
        return True

    # 遍历系统窗口，找Tooltip
    win32gui.EnumWindows(enum_tooltip_callback, tooltip_hwnds)
    
    # 逐个获取Tooltip窗口的文本（可能有多个，取非空的）
    for hwnd in tooltip_hwnds:
        text = win32gui.GetWindowText(hwnd)
        if text:  # 只取有内容的提示
            tooltip_text = text
            break
    return tooltip_text

time.sleep(1.0)
keyboard.send('win+m')
t = 0
while(t<8):
    t += 1
    print(f"\n 现在是第{t}次循环:")

    # 步骤0: 模拟按键选择窗口
    time.sleep(0.5)
    keyboard.send('tab')
    time.sleep(1.0)

    # 步骤1: 获取前台窗口线程ID（语法）
    print("step 1: 获取前台窗口线程ID")
    hwnd_foreground = win32gui.GetForegroundWindow()  # 获取前台窗口句柄
    thread_id, process_id = win32process.GetWindowThreadProcessId(hwnd_foreground)  # 提取线程ID
    print(f"\t 聚焦窗口的句柄:{hwnd_foreground}")
    print(f"\t 线程ID:{thread_id}")
    print(f"\t 进程ID:{process_id}")


    # 步骤2: 初始化结构体（语法）
    print("step 2: 初始化结构体")
    gti = GUIThreadInfo()
    gti.cbSize = ctypes.sizeof(GUIThreadInfo)  # 必须赋值，固定语法
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.GetGUIThreadInfo(thread_id, ctypes.byref(gti))
    focus_class = win32gui.GetClassName(gti.hwndFocus)
    print(f"\t 聚焦窗口的类:{focus_class}")

    # 步骤3: 获取对应文本
    print("step 3: 获取对应文本")
    tooltip_text = get_tooltip_text()
    tooltip_text = tooltip_text if tooltip_text else "无文本"
    windows_text = win32gui.GetWindowText(gti.hwndFocus)
    windows_text = windows_text if windows_text else "无文本"
    class_name = win32gui.GetClassName(gti.hwndFocus)
    class_name = class_name if class_name else "无?!"
    print(f"\t 工具提示控件的文本:{tooltip_text}")
    print(f"\t 窗口标题:{windows_text}")
    print(f"\t 窗口类名:{class_name}")

    # 获取焦点控件
    iuia = IUIA()
    element = iuia.get_focused_element()

    if element:
        # 提取信息
        display_text = element.CurrentName or "无文本"
        tooltip_text = element.CurrentHelpText or "无文本"
        control_type = iuia.known_control_types.get(element.CurrentControlType, "未知")
        control_name = display_text
        
        # 获取父窗口标题
        try:
            parent = element.GetParentElement()
            parent_window_title = parent.CurrentName if parent else "无父窗口"
        except:
            parent_window_title = "无?!"
    else:
        display_text = "无文本"
        tooltip_text = "无文本"
        control_type = "无?!"
        control_name = "无文本"
        parent_window_title = "无?!"

    # 输出
    print(f"\t 窗口文本:{display_text}")
    print(f"\t 悬浮文本:{tooltip_text}")
    print(f"\t 控件类型:{control_type}")
    print(f"\t 控件名称:{control_name}")
    print(f"\t 控件所属窗口标题:{parent_window_title}")
    if  "通知 V 形" in control_name:
        break
    time.sleep(1.0)

t = 0
while(t<8):
    t += 1
    print(f"\n 现在是第{t}次循环:")

    # 步骤0: 模拟按键选择窗口
    time.sleep(0.5)
    keyboard.send('right')
    time.sleep(1.0)

    # 步骤1: 获取前台窗口线程ID（语法）
    print("step 1: 获取前台窗口线程ID")
    hwnd_foreground = win32gui.GetForegroundWindow()  # 获取前台窗口句柄
    thread_id, process_id = win32process.GetWindowThreadProcessId(hwnd_foreground)  # 提取线程ID
    print(f"\t 聚焦窗口的句柄:{hwnd_foreground}")
    print(f"\t 线程ID:{thread_id}")
    print(f"\t 进程ID:{process_id}")

    # 步骤2: 初始化结构体（语法）
    print("step 2: 初始化结构体")
    gti = GUIThreadInfo()
    gti.cbSize = ctypes.sizeof(GUIThreadInfo)  # 必须赋值，固定语法
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.GetGUIThreadInfo(thread_id, ctypes.byref(gti))
    focus_class = win32gui.GetClassName(gti.hwndFocus)
    print(f"\t 聚焦窗口的类:{focus_class}")

    # 步骤3: 获取对应文本
    print("step 3: 获取对应文本")
    tooltip_text = get_tooltip_text()
    tooltip_text = tooltip_text if tooltip_text else "无文本"
    windows_text = win32gui.GetWindowText(gti.hwndFocus)
    windows_text = windows_text if windows_text else "无文本"
    class_name = win32gui.GetClassName(gti.hwndFocus)
    class_name = class_name if class_name else "无?!"
    print(f"\t 工具提示控件的文本:{tooltip_text}")
    print(f"\t 窗口标题:{windows_text}")
    print(f"\t 窗口类名:{class_name}")

    # 获取焦点控件
    iuia = IUIA()
    element = iuia.get_focused_element()

    if element:
        # 提取信息
        display_text = element.CurrentName or "无文本"
        tooltip_text = element.CurrentHelpText or "无文本"
        control_type = iuia.known_control_types.get(element.CurrentControlType, "未知")
        control_name = display_text
        
        # 获取父窗口标题
        try:
            parent = element.GetParentElement()
            parent_window_title = parent.CurrentName if parent else "无父窗口"
        except:
            parent_window_title = "无?!"
    else:
        display_text = "无文本"
        tooltip_text = "无文本"
        control_type = "无?!"
        control_name = "无文本"
        parent_window_title = "无?!"

    # 输出
    print(f"\t 窗口文本:{display_text}")
    print(f"\t 悬浮文本:{tooltip_text}")
    print(f"\t 控件类型:{control_type}")
    print(f"\t 控件名称:{control_name}")
    print(f"\t 控件所属窗口标题:{parent_window_title}")
    if "QQ" in control_name:
        break
    time.sleep(1.0)


time.sleep(0.5)
keyboard.send('win+shift+m')
time.sleep(1.0)