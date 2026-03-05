from contextlib import contextmanager
from playwright.sync_api import sync_playwright


@contextmanager
def session(url: str = "http://localhost:9222"):
    """CDP 会话上下文管理器"""
    p = sync_playwright().start()
    browser = p.chromium.connect_over_cdp(url)
    page = browser.contexts[0].pages[-1]
    
    try:
        yield page
    finally:
        browser.close()
        p.stop()