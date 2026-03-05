CDP_URL = "http://localhost:9222"
MESSAGE_SELECTOR = ".chat-message__content"
INPUT_SELECTOR = ".chat-input textarea"
CHECK_INTERVAL = 1.0

REPLY_RULES = {
    r"你好|您好": "你好！有什么可以帮您？",
    r"在吗|在不在": "在的，请说~",
    r"价格|多少钱": "请咨询客服获取报价",
}