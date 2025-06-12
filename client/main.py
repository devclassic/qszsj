from dotenv import load_dotenv
import os
import webview

load_dotenv()
url = os.getenv("URL")
webview.create_window("智慧政务", url, width=1280, height=750, resizable=False)
webview.start(private_mode=False)
