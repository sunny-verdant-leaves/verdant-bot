# 导入所需库（uiautomation小写，win32gui用于遍历Tooltip）
import uiautomation as auto
import win32gui
import time

def get_control_and_tooltip_text():
    """
    核心功能：
    1. 获取Tab/鼠标聚焦控件的名称（如“通知 V 形”）
    2. 获取该控件的悬浮提示文本（如“显示隐藏的图标”）
    """
    # ==================== 第一步：获取聚焦控件名称（核心） ====================
    control_name = "无"
    try:
        # 获取当前聚焦的控件（uiautomation官方方法）
        focused_control = auto.GetFocusedControl()
        # 提取控件名称（对应“通知 V 形”）
        control_name = focused_control.Name if focused_control else "无"
    except Exception as e:
        print(f"⚠️ 获取控件名时出错：{e}")

    # ==================== 第二步：获取悬浮提示（Tooltip）文本 ====================
    tooltip_text = "无"
    # 存储所有Tooltip窗口句柄（类名固定为tooltips_class32）
    tooltip_hwnds = []

    # 回调函数：遍历所有窗口，筛选Tooltip窗口
    def enum_tooltip_callback(hwnd, extra_list):
        # 只筛选可见的、类名为tooltips_class32的窗口
        if win32gui.GetClassName(hwnd) == "tooltips_class32" and win32gui.IsWindowVisible(hwnd):
            extra_list.append(hwnd)
        return True

    # 等待Tooltip弹出（关键：给0.8秒让系统显示悬浮提示）
    time.sleep(0.8)
    # 遍历系统所有窗口，收集Tooltip句柄
    win32gui.EnumWindows(enum_tooltip_callback, tooltip_hwnds)

    # 从Tooltip窗口中提取文本
    for hwnd in tooltip_hwnds:
        temp_text = win32gui.GetWindowText(hwnd)
        if temp_text and temp_text != "":  # 只取非空的提示文本
            tooltip_text = temp_text
            break

    # ==================== 返回最终结果 ====================
    return {
        "聚焦控件名称": control_name,
        "悬浮提示文本": tooltip_text
    }

# ==================== 主程序（运行入口） ====================
if __name__ == "__main__":
    # 提示用户操作
    print("📢 操作指引：")
    print("1. 先将鼠标/Tab键聚焦到任务栏右下角的“通知 V 形”按钮")
    print("2. 保持鼠标悬浮在按钮上，让“显示隐藏的图标”提示弹出来")
    print("3. 等待2秒后开始获取文本...\n")
    
    # 给用户5秒时间完成聚焦+悬浮操作
    time.sleep(5)
    
    # 调用核心函数获取文本
    result = get_control_and_tooltip_text()
    
    # 打印最终结果（格式化输出，清晰易读）
    print("✅ 获取结果：")
    for key, value in result.items():
        print(f"   {key}：{value}")