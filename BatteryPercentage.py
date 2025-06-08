import os
import sys
import psutil
import shutil
import datetime
from time import sleep
from pathlib import Path
from dotenv import load_dotenv
import threading
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw

# Load .env file
load_dotenv()

# Constants from environment variables
LOG_DIR = Path("Log")
MAXIMUM = int(os.getenv("maximum", 90))
MINIMUM = int(os.getenv("minimum", 20))
    
LOG_LABEL = "Live"
PAUSE_FILE = Path("pause_flag.txt")

# Notification Setup
platform = sys.platform
USE_WIN_TOAST = platform.startswith("win")
if USE_WIN_TOAST:
    from winotify import Notification, audio
else:
    from plyer import notification

def get_log_path() -> Path:
    date_str = datetime.datetime.now().strftime("%d-%m-%Y")
    daily_log_dir = LOG_DIR / date_str
    daily_log_dir.mkdir(parents=True, exist_ok=True)
    return daily_log_dir

def cleanup_logs(retention_days: int = 5) -> None:
    if not LOG_DIR.exists():
        return
    threshold_date = datetime.datetime.now().date() - datetime.timedelta(days=retention_days)
    for entry in LOG_DIR.iterdir():
        if entry.is_dir():
            try:
                dir_date = datetime.datetime.strptime(entry.name, "%d-%m-%Y").date()
                if dir_date <= threshold_date:
                    shutil.rmtree(entry)
            except ValueError:
                shutil.rmtree(entry)

def write_log(file_name: str, data: str) -> None:
    log_path = get_log_path() / f"{file_name}.txt"
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} {data}\n")
    except Exception as e:
        print(f"Failed to write log: {e}")

# Enforce minimum interval of 30 seconds
raw_interval = int(os.getenv("interval", 30))
INTERVAL = max(raw_interval, 30)
if raw_interval < 30:
    write_log(LOG_LABEL, "[WARNING] Interval too low. Enforcing minimum of 30 seconds.")

def get_icon_path() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), "logo.ico")
    return os.path.join(os.path.dirname(__file__), "logo.ico")

def show_notification(title: str, message: str, icon_path: str = "") -> None:
    def notify():
        if USE_WIN_TOAST:
            toast = Notification(
                app_id="BatteryNotifier",
                title=title,
                msg=message,
                icon=icon_path if os.path.exists(icon_path) else None
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()
        else:
            notification.notify(
                title=title,
                message=message,
                app_name="BatteryNotifier",
                timeout=10,
                app_icon=icon_path if os.path.exists(icon_path) else None
            )
    threading.Thread(target=notify, daemon=True).start()

def is_paused() -> bool:
    if not PAUSE_FILE.exists():
        return False
    try:
        with open(PAUSE_FILE, "r") as f:
            content = f.read().strip()
            if content == "charge":
                battery = psutil.sensors_battery()
                return battery and not battery.power_plugged
            elif content.startswith("pause_until:"):
                pause_until = float(content.split(":")[1])
                return datetime.datetime.now().timestamp() < pause_until
    except Exception as e:
        write_log(LOG_LABEL, f"Pause check error: {e}")
    return False

def set_pause_for_5_minutes():
    pause_until = datetime.datetime.now().timestamp() + 5 * 60
    with open(PAUSE_FILE, "w") as f:
        f.write(f"pause_until:{pause_until}")

def set_pause_until_plugged():
    with open(PAUSE_FILE, "w") as f:
        f.write("charge")

def clear_pause():
    if PAUSE_FILE.exists():
        PAUSE_FILE.unlink()

def monitor_battery() -> None:
    battery = psutil.sensors_battery()
    if battery is None:
        write_log(LOG_LABEL, "No battery information available.")
        return

    icon = get_icon_path()

    if battery.percent >= MAXIMUM and battery.power_plugged:
        show_notification("Battery Alert Notification", f"Battery full {battery.percent}% - Unplug your charger", icon)
        write_log(LOG_LABEL, f"Battery full at {battery.percent}% - Unplug your charger.")
    elif battery.percent <= MINIMUM and not battery.power_plugged:
        show_notification("Battery Alert Notification", f"Battery Low {battery.percent}% - Connect your charger", icon)
        write_log(LOG_LABEL, f"Battery low at {battery.percent}% - Connect your charger.")
    elif battery.percent >= MAXIMUM:
        write_log(LOG_LABEL, f"Battery almost fully charged: {battery.percent}%.")
    else:
        clear_pause()
        write_log(LOG_LABEL, f"Battery at {battery.percent}%. Not yet fully charged.")

def main():
    while True:
        try:
            if not is_paused():
                monitor_battery()
                cleanup_logs()
        except Exception as e:
            write_log(LOG_LABEL, f"Unhandled error: {e}")
        sleep(INTERVAL)

# --- System Tray Icon Code ---
def create_image() -> Image.Image:
    img = Image.new('RGB', (64, 64), color='white')
    d = ImageDraw.Draw(img)
    d.rectangle([10, 20, 54, 44], fill='green', outline='black')
    d.rectangle([54, 28, 58, 36], fill='black')
    return img

def on_pause_5_minutes(icon, item):
    set_pause_for_5_minutes()
    show_notification("BatteryNotifier", "Paused for 5 minutes", get_icon_path())

def on_pause_until_plugged(icon, item):
    set_pause_until_plugged()
    show_notification("BatteryNotifier", "Paused until plugged", get_icon_path())

def on_resume(icon, item):
    clear_pause()
    show_notification("BatteryNotifier", "Notifications resumed", get_icon_path())

def on_exit(icon, item):
    icon.stop()
    os._exit(0)

def run_tray():
    menu = Menu(
        MenuItem("Pause 5 Minutes", on_pause_5_minutes),
        MenuItem("Pause Until plugged", on_pause_until_plugged),
        MenuItem("Resume Notifications", on_resume),
        MenuItem("Exit", on_exit)
    )
    icon = Icon("Battery Monitor", create_image(), menu=menu, title="Battery Monitor")
    icon.run()

if __name__ == "__main__":
    tray_thread = threading.Thread(target=run_tray, daemon=True)
    tray_thread.start()
    main()
