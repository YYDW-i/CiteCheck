import threading
import time
import webbrowser
import traceback

def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000/login")

if __name__ == "__main__":
    try:
        from app.main import app
        import uvicorn

        threading.Thread(target=open_browser, daemon=True).start()
        uvicorn.run(app, host="127.0.0.1", port=8000)

    except Exception:
        traceback.print_exc()
        input("\n启动失败，按回车退出...")