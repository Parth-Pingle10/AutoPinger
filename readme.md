# 🚀 Auto Pinger (FastAPI)

An async auto-pinger service built with FastAPI that continuously sends requests to a given URL to keep services alive.

---

## ✨ Features

* 🔁 Periodic HTTP ping (every ~8 minutes)
* ⚡ Fully async using `asyncio` + `httpx`
* 🌐 Dynamic URL input via endpoint
* ▶️ Start and ⏹️ stop pingers via API
* 🧠 Background task handling using `asyncio.create_task`
* 🛑 Graceful cancellation using `CancelledError`

---

## 🏗️ Tech Stack

* FastAPI
* httpx (Async HTTP client)
* asyncio (Python async runtime)

---

## 📦 Installation

```bash
git clone https://github.com/your-username/auto-pinger.git
cd auto-pinger

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install fastapi uvicorn httpx
```

---

## 🚀 Run the server

```bash
uvicorn main:app --reload
```

Server will start at:

```
http://127.0.0.1:8000
```

---

## 📡 API Usage

### ▶️ Start Pinging

```
GET /start/{url}
```

Example:

```
http://127.0.0.1:8000/start/google.com
```

---

### ⏹️ Stop Pinging

```
GET /stop/{url}
```

Example:

```
http://127.0.0.1:8000/stop/google.com
```

---

## 🧠 How It Works

* Each URL starts a **background async task**
* Tasks run in an infinite loop:

  * Send request
  * Wait
  * Repeat
* Active tasks are stored in-memory
* Tasks can be cancelled safely using `task.cancel()`

---

## ⚠️ Limitations

* ❌ Tasks are not persisted (lost on server restart)
* ❌ No authentication (anyone can trigger endpoints)
* ❌ Not suitable for large-scale production use (yet)

---

## 🔮 Future Improvements

* Add database (store URLs persistently)
* Auto-restart tasks on server boot
* Add authentication / API keys
* Build frontend dashboard
* Rate limiting & abuse protection

---

## 🤝 Contributing

Pull requests are welcome. Feel free to open issues or suggest improvements.

---

## 📄 License

MIT License

---

## 💡 Inspiration

Built as a lightweight alternative to uptime monitoring tools for learning async systems and background task management.
