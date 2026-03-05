from dataclasses import dataclass
from typing import Optional
from playwright.sync_api import Page


@dataclass
class Message:
    raw: str
    content: str


def fetch_last(page: Page, selector: str) -> Optional[Message]:
    """获取最后一条消息"""
    elements = page.query_selector_all(selector)
    if not elements:
        return None
    
    raw = elements[-1].inner_text()
    # 简单清理：取最后一行作为内容
    content = raw.split("\n")[-1].strip()
    
    return Message(raw=raw, content=content)