# 🐼 ARIA — Personal Research Assistant Agent

ARIA (Advanced Research & Information Assistant) is an AI-powered chatbot built with LangChain and LangGraph. It uses the ReAct pattern (Reason + Act) to think through your questions, pick the right tool, and give clear answers. ARIA remembers everything you say during a conversation and streams its thinking in real time.

## 🛠️ Tools Implemented

| # | Tool | What it does |
|---|------|-------------|
| 1 | `search_wikipedia` | Searches Wikipedia and returns a summary of any topic |
| 2 | `get_current_time` | Returns the current date and time for any timezone |
| 3 | `calculate` | Safely evaluates math expressions including percentages |
| 4 | `get_weather` | Fetches live weather using wttr.in — no API key needed |
| 5 | `save_note` | Saves any text as a .txt file in a local notes/ folder |
| 6 | `generate_password` | Generates a strong random password |

## ✅ Bonus Features

- 🧠 Conversation Memory — ARIA remembers everything said earlier using MemorySaver
- 📡 Streaming Mode — Watch ARIA think step by step as it runs tools
- 📝 File Writing Tool — save_note writes research findings to local .txt files
- 🔒 Input Validation — All tools validate inputs and return helpful error messages
- 💻 Runs Locally — Uses Ollama with Llama 3.2, no API key or internet needed!

## 🚀 How to Run

### Prerequisites
- Python 3.10+
- Git
- Ollama installed from https://ollama.com (free, no API key needed)
- OR an OpenAI API key from https://platform.openai.com (paid)

### Step 1 — Clone the repo
```
git clone https://github.com/YourUsername/langchain-agent-homework.git
cd langchain-agent-homework
```

### Step 2 — Create virtual environment
```
python -m venv venv
venv\Scripts\activate
```

### Step 3 — Install packages
```
pip install -r requirements.txt
```

### Step 4 — Download the AI model
```
ollama pull llama3.2
```

### Step 5 — Run the agent
```
python agent.py
```

## 💬 Example Conversation
```
You: What time is it in Tokyo?

ARIA:
  🔧 [Using tool: get_current_time]
The current time in Tokyo is 11:31 PM. Is there anything else you'd like to know?

You: Tell me about the Eiffel Tower

ARIA:
  🔧 [Using tool: search_wikipedia]
The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France.
It was constructed from 1887 to 1889 as the centerpiece of the 1889 World's Fair.

You: What is 15% of 340?

ARIA:
  🔧 [Using tool: calculate]
15% of 340 = 51.0

You: What is the weather in Paris?

ARIA:
  🔧 [Using tool: get_weather]
🌤️ Weather in Paris, France
- Condition: Partly Cloudy
- Temperature: 12°C / 53°F
- Humidity: 65%

You: Save a note about everything we discussed

ARIA:
  🔧 [Using tool: save_note]
✅ Note saved successfully!

You: Generate me a strong password

ARIA:
  🔧 [Using tool: generate_password]
🔐 Generated Password: xK9$mPq!2rLv#Tz8
- Strength: Strong 💪
```

## 💭 Reflection

The most interesting thing I learned was the ReAct (Reason + Act) pattern — the AI automatically decides which tool to use just by reading the function descriptions, without any extra logic needed. The hardest part was getting the API keys set up, which is why I switched to Ollama so the agent runs completely free and offline. If I had more time I would add a news search tool and a tool that reads back saved notes so ARIA can reference previous research sessions.

## 📦 Tech Stack

- LangChain — Tool definitions and LLM wrappers
- LangGraph — create_react_agent and MemorySaver
- Ollama + Llama 3.2 — Free local AI, no API key needed (fallback)
- OpenAI GPT-4o — Paid option, just add your key to .env
- wttr.in — Free weather API
- Wikipedia API — Free encyclopedia search