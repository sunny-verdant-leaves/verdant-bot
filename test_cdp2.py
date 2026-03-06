# test_qq_full.py - 获取 QQ 账号、好友/群名

import time
import win32api
import win32gui
import win32process
import psutil
import keyboard
import uiautomation as auto

QQ_CLASS = "Chrome_WidgetWin_1"

import win32gui
import win32process
import psutil

# 定义QQ的类名常量
QQ_CLASS = "Chrome_WidgetWin_1"

def get_qq_windows():
    """
    修复版：获取所有 QQ 相关窗口（含深层级子窗口），输入输出与原版本完全一致
    关键修复：递归枚举所有子窗口、兼容多进程、放宽类名筛选
    """
    qq_windows = []

    # ---------- 辅助函数：获取窗口所属进程ID ----------
    def _get_window_pid(hwnd):
        try:
            tid, pid = win32process.GetWindowThreadProcessId(hwnd)
            return pid
        except Exception:
            return None

    # ---------- 辅助函数：判断进程是否属于QQ（兼容多进程） ----------
    def _is_qq_process(pid):
        """不止匹配主进程PID，而是判断进程名是否含QQ"""
        if not pid:
            return False
        try:
            proc_name = psutil.Process(pid).name()
            return "QQ" in proc_name  # 兼容主进程/渲染进程
        except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
            return False

    # ---------- 核心修复：递归枚举所有层级的子窗口 ----------
    def _enum_all_child_windows(parent_hwnd, all_child_hwnds):
        """递归枚举parent_hwnd下所有层级的子窗口，存入all_child_hwnds"""
        def _child_callback(child_hwnd, extra):
            if not child_hwnd:
                return True
            
            # 过滤条件1：窗口可见（必选，排除隐藏窗口）
            if not win32gui.IsWindowVisible(child_hwnd):
                return True
            
            # 过滤条件2：属于QQ进程（兼容多进程，替代原PID严格匹配）
            child_pid = _get_window_pid(child_hwnd)
            if not _is_qq_process(child_pid):
                return True
            
            # 过滤条件3：放宽类名筛选（保留核心CEF类名，增加通配）
            child_class = win32gui.GetClassName(child_hwnd)
            cef_keywords = ["Chrome", "Cef", "QQ", "TX"]  # 关键词匹配，而非固定类名
            if not any(keyword in child_class for keyword in cef_keywords):
                return True
            
            # 满足条件则加入列表
            all_child_hwnds.append(child_hwnd)
            
            # 递归枚举当前子窗口的子窗口（核心！遍历所有层级）
            _enum_all_child_windows(child_hwnd, all_child_hwnds)
            return True

        win32gui.EnumChildWindows(parent_hwnd, _child_callback, None)

    # ---------- 主逻辑：枚举所有QQ窗口 ----------
    def _enum_windows_callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return True
        
        class_name = win32gui.GetClassName(hwnd)
        title = win32gui.GetWindowText(hwnd)
        
        # 筛选QQ主窗口（类名匹配 + 进程匹配）
        if class_name == QQ_CLASS:
            pid = _get_window_pid(hwnd)
            if not _is_qq_process(pid):
                return True
            
            # 修复核心：递归枚举所有层级子窗口
            child_hwnds = []
            _enum_all_child_windows(hwnd, child_hwnds)  # 替代原一级枚举
            
            qq_windows.append({
                'hwnd': hwnd,
                'title': title,
                'pid': pid,
                'is_main': title == "QQ",
                'child_hwnds': child_hwnds  # 现在能拿到所有层级的有效子窗口
            })
            # 调试日志：方便排查
            print(f"找到QQ窗口：句柄={hwnd}，子窗口数量={len(child_hwnds)}")
        return True

    # 执行枚举
    win32gui.EnumWindows(_enum_windows_callback, None)
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
    time.sleep(5.0)
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
        time.sleep(1.5)
    
    for w in windows:
        w["uia_windows"] = auto.ControlFromHandle(w["hwnd"])
        w["uia_windows"].SetActive()
    windows = get_qq_windows()
    print(windows)
    
    for w in windows:
        # print(w)
        # for key in w:
        #     print(f"{key}: {w[key]}")
        print(w["hwnd"])
        print(w["child_hwnds"])
        w["uia_windows"] = auto.ControlFromHandle(w["hwnd"])
        w["uia_windows"].Minimize()
        w["child_windows"] = auto.ControlFromHandle(w["child_hwnds"][0])
        print(w["child_windows"])

        def traverse_qq_controls_compatible(control, depth=0, file=None, index_path=None):
            """
            最终优化版：新增层级索引路径+保持原参数一致+写入文件（无终端刷屏）
            参数（与原函数完全一致，主函数无需修改）：
                control: uiautomation控件对象（起始遍历的控件）
                depth: 递归层级（无需手动传，默认0）
            内部参数（自动处理）：
                file: 文件句柄（避免重复IO）
                index_path: 索引路径（如[0][1]，记录控件在层级中的位置）
            输出：控件信息+索引路径写入 qq_controls_log.txt
            """
            # 初始化文件句柄（仅第一层递归）
            if file is None:
                file = open("qq_controls_log.txt", "w", encoding="utf-8")
                file.write("===== QQ控件遍历日志（含索引路径） =====\n")
            
            # 初始化索引路径（仅第一层递归，初始为空列表）
            if index_path is None:
                index_path = []

            indent = "  " * depth
            # 基础信息（兼容缺失属性）
            ctrl_name = getattr(control, "Name", "无")
            ctrl_type = getattr(control, "ControlType", "未知")
            ctrl_enabled = getattr(control, "IsEnabled", "未知")
            
            # 生成索引路径字符串（如 [0][1][2]）
            index_str = "".join([f"[{idx}]" for idx in index_path]) if index_path else "[根节点]"
            # 控件类型中文标注
            type_cn = "面板(Pane)" if ctrl_type == 50033 else f"其他({ctrl_type})"
            
            # 写入文件（新增索引路径，格式更清晰）
            log_line = (
                f"{indent}索引路径：{index_str} | 层级{depth} | 名称：{ctrl_name} "
                f"| 类型：{type_cn} | 可用：{ctrl_enabled}\n"
            )
            file.write(log_line)

            # 递归遍历子控件（记录每一层的索引）
            try:
                children = control.GetChildren()
                # 遍历子控件时，记录当前子控件的索引（0,1,2...）
                for child_idx, child in enumerate(children):
                    # 拼接索引路径：父路径 + 当前子控件索引
                    new_index_path = index_path + [child_idx]
                    traverse_qq_controls_compatible(child, depth + 1, file, new_index_path)
            except Exception as e:
                # 异常信息也包含索引路径，方便定位问题控件
                error_line = f"{indent}⚠️ 索引路径：{index_str} | 层级{depth}控件无子控件：{str(e)}\n"
                file.write(error_line)
            
            # 仅第一层递归结束时关闭文件
            if depth == 0:
                file.close()
                print(f"✅ 控件遍历完成！日志已写入：qq_controls_log.txt")

        def get_control_by_index_path(control, index_path):
            """
            根据索引路径定位目标控件（与traverse_qq_controls_compatible的索引逻辑完全匹配）
            参数：
                control: 起始控件（如QQ主窗口控件，uiautomation对象）
                index_path: 索引路径列表（如[0,3,2]，对应日志中的[0][3][2]）
            返回：
                成功：目标控件对象 | 失败：None
            异常处理：兼容索引越界、控件无子孙、GetChildren失败等场景
            """
            current_ctrl = control
            
            for idx in index_path:
                try:
                    # 获取当前控件的所有子控件
                    children = current_ctrl.GetChildren()
                    # 检查索引是否越界
                    if idx < 0 or idx >= len(children):
                        print(f"❌ 索引越界：当前层级只有{len(children)}个子控件，无法获取索引{idx}")
                        return None
                    # 定位到下一层级的目标子控件
                    current_ctrl = children[idx]
                except AttributeError:
                    print(f"❌ 索引{idx}对应的控件无GetChildren方法（非容器控件）")
                    return None
                except Exception as e:
                    print(f"❌ 定位索引{idx}失败：{str(e)}")
                    return None
            
            # 返回最终定位到的控件
            print(f"✅ 成功定位控件：名称={getattr(current_ctrl, 'Name', '无')} | 类型={getattr(current_ctrl, 'ControlType', '未知')}")
            return current_ctrl
        
        # 执行遍历，打印所有组件特征（运行后查看输出，找到目标组件的特征）
        print("=== QQ根面板下所有组件特征（层级展示）===")
        traverse_qq_controls_compatible(w["child_windows"], file=open("./logs/qq_controls_log.txt", "w", encoding="utf-8"))

        message_list_ctrl = get_control_by_index_path(w["child_windows"], [0, 1, 2, 0, 0, 0, 0])
        print(message_list_ctrl)
        w["uia_windows"].SetActive()
        orig_mouse_x, orig_mouse_y = win32api.GetCursorPos()    # 保存鼠标原始坐标
        message_list_ctrl.Click(simulateMove=False)
        win32api.SetCursorPos((orig_mouse_x, orig_mouse_y))     # 恢复鼠标原始坐标
        time.sleep(0.5)

        orig_mouse_x, orig_mouse_y = win32api.GetCursorPos()
        message_ctrl = get_control_by_index_path(w["child_windows"], [0, 1, 3, 0, 0, 2, 0, 2, 0, 1, 0])
        message_ctrl.Click(simulateMove=False)
        win32api.SetCursorPos((orig_mouse_x, orig_mouse_y))
        message_ctrl = get_control_by_index_path(w["child_windows"], [0, 1, 3, 0, 0, 2, 0, 3, 0, 1, 0])
        message_ctrl.Click(simulateMove=False)
        win32api.SetCursorPos((orig_mouse_x, orig_mouse_y))
        time.sleep(0.5)

        orig_mouse_x, orig_mouse_y = win32api.GetCursorPos()
        message_ctrl = get_control_by_index_path(w["child_windows"], [0, 1, 3, 1, 1, 1, 3, 0])
        message_ctrl.Click(simulateMove=False)
        keyboard.send("w")
        time.sleep(0.05)
        keyboard.send("o")
        time.sleep(0.05)
        keyboard.send("a")
        time.sleep(0.05)
        keyboard.send("i")
        time.sleep(0.05)
        keyboard.send("n")
        time.sleep(0.05)
        keyboard.send("i")
        time.sleep(0.05)
        keyboard.send("space")
        time.sleep(0.5)
        keyboard.send("ctrl+enter")
        time.sleep(1.5)
        win32api.SetCursorPos((orig_mouse_x, orig_mouse_y))
        w["uia_windows"].Minimize()
        
        traverse_qq_controls_compatible(w["child_windows"], file=open("./logs/qq_controls_log3.txt", "w", encoding="utf-8"))


        
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
        # w["uia_windows"].SetActive()
        # focused_ctrl = None
        # for i in range(1,11):
        #     focused_ctrl = auto.GetFocusedControl()
        #     if not focused_ctrl:
        #         print(f"第{i}个控件不存在/未聚焦")
        #         continue
        #     print(f"\n 第{i}个控件为{focused_ctrl.Name}")
        #     print(focused_ctrl)
        #     traverse_qq_controls_compatible(focused_ctrl)
        #     # if "的头像" in focused_ctrl.Name:
        #     #     # print(focused_ctrl)

        #     time.sleep(0.1)
        #     keyboard.send('tab')

    analyze_qq_windows(windows)

if __name__ == "__main__":
    test()