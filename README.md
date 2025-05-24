# 🔋 Battery Alert Notifier (Python)

A simple yet effective desktop notifier tool that monitors your battery percentage and alerts you when it's too low or fully charged. Helps extend battery health and avoid power surprises.

---

## ⚙️ Features

- 📢 Notification on full charge (above `maximum` %)
- 📢 Notification on low battery (below `minimum` %)
- 📝 Logs all events with timestamps in date-wise folders
- ⚙️ Configurable thresholds and interval via `.env`
- 💻 Works silently in the background
- 🖼️ Tray notifications with custom icons

---

## 🧪 How to Use

### 1. Clone the Repo
```bash
git clone https://github.com/raquib-dev/battery-alert-notifier.git
cd battery-alert-notifier
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file (optional)
```ini
maximum=90
minimum=20
interval=15
```

### 4. Run the App
```bash
python main.py
```

---

## 🛠 Tech Stack

- `Python 3.10+`
- `psutil` – For battery stats
- `plyer` – For cross-platform notifications
- `dotenv` – For environment variable config
- `tkinter` – To register tray icon (on some systems)

---

## 📁 Project Structure

```
.
├── main.py
├── logo.ico
├── requirements.txt
├── .env
├── Log/
└── .gitignore
```

---

## ✅ Use Cases

- Prevent overcharging laptop batteries
- Avoid sudden shutdowns due to low battery
- Quiet background notifier with logs

---

## 🧹 Log Retention

- Logs are stored in `Log/{dd-mm-yyyy}/`
- Automatically deletes logs older than 5 days

---

## 🚀 Tip

Package it with `pyinstaller` to run as a background Windows/Linux/Tray App:

```bash
pyinstaller --onefile --windowed main.py --icon=logo.ico
```
