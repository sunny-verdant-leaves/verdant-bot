import time
from verdantbot import config
from verdantbot.utils.cdp_client import session
from verdantbot.core.fetcher import fetch_last
from verdantbot.core.processor import process
from verdantbot.core.sender import send


def main():
    print(f"Connecting to {config.CDP_URL}...")
    
    with session(config.CDP_URL) as page:
        print("Connected! Bot running...")
        last_raw = None
        
        while True:
            msg = fetch_last(page, config.MESSAGE_SELECTOR)
            
            if msg and msg.raw != last_raw:
                last_raw = msg.raw
                print(f"收到: {msg.content}")
                
                reply = process(msg.content, config.REPLY_RULES)
                if reply:
                    success = send(page, config.INPUT_SELECTOR, reply.text)
                    print(f"回复: {reply.text} ({'ok' if success else 'fail'})")
            
            time.sleep(config.CHECK_INTERVAL)


if __name__ == "__main__":
    main()