import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class Reply:
    text: str


def process(message: str, rules: dict[str, str]) -> Optional[Reply]:
    """根据规则匹配回复"""
    for pattern, reply_text in rules.items():
        if re.search(pattern, message, re.IGNORECASE):
            return Reply(text=reply_text)
    return None