# 🌦️ Weather Chatbot with Gemini + OpenWeather

This is a **local web app** that integrates:

* **Gemini AI** → to answer general questions and act as the chatbot brain.
* **OpenWeather API** → to fetch real-time weather details.
* **FastAPI backend** → to connect AI + weather API.

---

## 📂 Project Structure

```
WEATHER-CHATBOT/
│── agents/
│   │── __init__.py
│   │── gemini_client.py      # Gemini integration
│   │── tools.py              # OpenWeather API wrapper
│   │── weather_agent.py      # Handles chatbot logic
│── static/
│   │── index.html            # Chat UI
│── main.py                   # FastAPI entry point
│── requirements.txt          # Dependencies
│── README.md                 # Project docs
│── .env                      # API keys (ignored by Git)
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/weather-chatbot.git
cd weather-chatbot
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate   # On Mac/Linux
.venv\Scripts\activate      # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root folder:

```
OPENWEATHER_API_KEY=your_openweather_api_key
GEMINI_API_KEY=your_gemini_api_key
```

🔑 Get keys here:

* OpenWeather: [https://openweathermap.org/api](https://openweathermap.org/api)
* Gemini API: [https://ai.google.dev](https://ai.google.dev)

---

## 🚀 Running the App

Start FastAPI backend:

```bash
uvicorn main:app --reload
```

Open your browser at:
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 💬 Features

* Chatbot responds to **general questions** using Gemini.
* Ask for **real-time weather** by typing messages like:

  * "What’s the weather in New York?"
  * "Tell me the temperature in Delhi"
* Simple browser-based UI (no React, no frameworks).
* Runs fully **local** (only API calls to Gemini & OpenWeather).

---

## 📦 Dependencies

* [FastAPI](https://fastapi.tiangolo.com/)
* [Uvicorn](https://www.uvicorn.org/)
* [Requests](https://docs.python-requests.org/)
* [Python-dotenv](https://pypi.org/project/python-dotenv/)
* [Google Generative AI SDK](https://ai.google.dev/)

Installed via:

```bash
pip install fastapi uvicorn requests python-dotenv google-generativeai
```
