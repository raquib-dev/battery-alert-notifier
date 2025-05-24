import os
import sys
import psutil
import shutil
import datetime
from time import sleep
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Constants from environment variables
LOG_DIR = Path("Log")
MAXIMUM = int(os.getenv("maximum", 90))
MINIMUM = int(os.getenv("minimum", 20))
INTERVAL = int(os.getenv("interval", 15))
LOG_LABEL = "Live"

# Determine notification backend
platform = sys.platform
USE_WIN_TOAST = platform.startswith("win")

# Notification Setup
if USE_WIN_TOAST:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
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

def get_icon_path() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), "logo.ico")
    return os.path.join(os.path.dirname(__file__), "logo.ico")

def show_notification(title: str, message: str, icon_path: str) -> None:
    if USE_WIN_TOAST:
        toaster.show_toast(title, message, icon_path=icon_path, duration=10)
    else:
        notification.notify(
            title=title,
            message=message,
            app_name="BatteryNotifier",
            timeout=10,
            app_icon=icon_path if os.path.exists(icon_path) else None
        )

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
        write_log(LOG_LABEL, f"Battery at {battery.percent}%. Not yet fully charged.")

def main():
    while True:
        try:
            monitor_battery()
            cleanup_logs()
        except Exception as e:
            write_log(LOG_LABEL, f"Unhandled error: {e}")
        sleep(INTERVAL)

if __name__ == "__main__":
    main()