from playwright.sync_api import Page


def send(page: Page, selector: str, text: str) -> bool:
    """发送消息"""
    try:
        input_box = page.query_selector(selector)
        if not input_box:
            return False
        
        input_box.fill(text)
        input_box.press("Enter")
        return True
    except Exception:
        return False