"""
Personal Research Assistant Agent
===================================
A smart AI agent with 6 custom tools, conversation memory,
and streaming output so you can watch it think step by step.
"""

import os
import math
import random
import string
import urllib.request
import urllib.parse
import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()


def get_llm():
    if os.getenv("OPENAI_API_KEY"):
        from langchain_openai import ChatOpenAI
        print("✅ Using OpenAI GPT-4o")
        return ChatOpenAI(model="gpt-4o", temperature=0)
    else:
        from langchain_ollama import ChatOllama
        print("✅ Using Ollama (llama3.2) — running locally!")
        return ChatOllama(model="llama3.2", temperature=0)


from langchain_core.tools import tool


@tool
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for factual information about any topic.
    Use this when the user asks factual questions about people,
    places, history, science, or any real-world topic.

    Args:
        query: The topic or question to search for on Wikipedia.
    """
    try:
        import wikipedia
        wikipedia.set_lang("en")
        results = wikipedia.search(query, results=3)
        if not results:
            return f"No Wikipedia results found for '{query}'."
        try:
            summary = wikipedia.summary(results[0], sentences=5, auto_suggest=False)
            page = wikipedia.page(results[0], auto_suggest=False)
            return f"📖 {page.title}\n\n{summary}\n\n🔗 Source: {page.url}"
        except wikipedia.DisambiguationError as e:
            summary = wikipedia.summary(e.options[0], sentences=5, auto_suggest=False)
            return f"📖 (Multiple results found, showing top match)\n\n{summary}"
    except ImportError:
        return "❌ Wikipedia package not installed. Run: pip install wikipedia"
    except Exception as e:
        return f"❌ Wikipedia search failed: {str(e)}"


@tool
def get_current_time(timezone: str = "UTC") -> str:
    """Get the current date and time for any location in the world.
    Use this when the user asks what time or date it is, or asks
    about time in a specific city or timezone.

    Args:
        timezone: Timezone name like 'America/New_York', 'Europe/London',
                  'Asia/Tokyo', or just 'UTC'. Defaults to UTC.
    """
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)
        formatted = now.strftime("%A, %B %d, %Y at %I:%M %p")
        return f"🕐 Current time in {timezone}: {formatted}"
    except Exception:
        now = datetime.utcnow()
        formatted = now.strftime("%A, %B %d, %Y at %I:%M %p")
        return (
            f"⚠️ Timezone '{timezone}' not recognized. Showing UTC instead:\n"
            f"🕐 {formatted} UTC\n\n"
            f"Tip: Use formats like 'America/New_York' or 'Asia/Tokyo'"
        )


@tool
def calculate(expression: str) -> str:
    """Safely calculate any math expression.
    Use this for arithmetic, algebra, percentages, or any math question.
    Examples: '2 + 2', '15% of 200', 'sqrt(144)', '2 ** 10'

    Args:
        expression: A math expression as a string to evaluate safely.
    """
    try:
        expr = expression.strip()
        if "% of" in expr.lower():
            parts = expr.lower().replace("% of", "").split()
            percent = float(parts[0])
            total = float(parts[1])
            result = (percent / 100) * total
            return f"🧮 {percent}% of {total} = {result}"
        try:
            import numexpr
            result = numexpr.evaluate(expr)
            return f"🧮 {expr} = {float(result)}"
        except ImportError:
            safe_names = {
                "sqrt": math.sqrt, "pi": math.pi, "e": math.e,
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "log": math.log, "log10": math.log10, "abs": abs,
                "round": round, "pow": pow, "floor": math.floor,
                "ceil": math.ceil,
            }
            result = eval(expr, {"__builtins__": {}}, safe_names)
            return f"🧮 {expr} = {result}"
    except ZeroDivisionError:
        return "❌ Cannot divide by zero!"
    except Exception as e:
        return f"❌ Could not calculate '{expression}': {str(e)}"


@tool
def get_weather(city: str) -> str:
    """Get the current weather for any city in the world.
    Use this when the user asks about weather, temperature, or
    conditions in a specific location.

    Args:
        city: The name of the city to get weather for (e.g., 'London', 'Tokyo').
    """
    try:
        city_encoded = urllib.parse.quote(city)
        url = f"https://wttr.in/{city_encoded}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "ResearchAgent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        current = data["current_condition"][0]
        area = data["nearest_area"][0]
        city_name = area["areaName"][0]["value"]
        country = area["country"][0]["value"]
        temp_c = current["temp_C"]
        temp_f = current["temp_F"]
        feels_c = current["FeelsLikeC"]
        feels_f = current["FeelsLikeF"]
        description = current["weatherDesc"][0]["value"]
        humidity = current["humidity"]
        wind_kmph = current["windspeedKmph"]
        return (
            f"🌤️ Weather in {city_name}, {country}\n\n"
            f"• Condition: {description}\n"
            f"• Temperature: {temp_c}°C / {temp_f}°F\n"
            f"• Feels like: {feels_c}°C / {feels_f}°F\n"
            f"• Humidity: {humidity}%\n"
            f"• Wind speed: {wind_kmph} km/h"
        )
    except Exception as e:
        return f"❌ Could not get weather for '{city}': {str(e)}"


@tool
def save_note(title: str, content: str) -> str:
    """Save a research note or any text to a local file for later use.
    Use this when the user wants to save information, create a note,
    write down research findings, or store any text they provide.

    Args:
        title: A short title for the note (used as the filename).
        content: The full text content to save in the note.
    """
    try:
        if not title or not title.strip():
            return "❌ Please provide a title for the note."
        if not content or not content.strip():
            return "❌ Please provide content to save."
        if len(content) > 100000:
            return "❌ Content is too long (max 100,000 characters)."
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
        safe_title = safe_title.strip().replace(" ", "_")[:50]
        filename = f"note_{safe_title}.txt"
        notes_dir = Path("notes")
        notes_dir.mkdir(exist_ok=True)
        filepath = notes_dir / filename
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Title: {title}\n")
            f.write(f"Saved: {timestamp}\n")
            f.write("-" * 40 + "\n\n")
            f.write(content)
        return (
            f"✅ Note saved successfully!\n"
            f"📁 File: {filepath}\n"
            f"📝 Title: {title}\n"
            f"📏 Characters saved: {len(content)}"
        )
    except Exception as e:
        return f"❌ Failed to save note: {str(e)}"


@tool
def generate_password(length: int = 16, include_symbols: bool = True) -> str:
    """Generate a strong, secure random password.
    Use this when the user asks for a password, wants a secure password,
    or needs help creating credentials.

    Args:
        length: How many characters long the password should be (default: 16).
        include_symbols: Whether to include symbols like !@#$% (default: True).
    """
    try:
        if length < 4:
            return "❌ Password must be at least 4 characters long."
        if length > 128:
            return "❌ Password length capped at 128 characters."
        chars = string.ascii_letters + string.digits
        if include_symbols:
            chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
        while True:
            password = "".join(random.choices(chars, k=length))
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_symbol = any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password)
            if include_symbols:
                if has_upper and has_lower and has_digit and has_symbol:
                    break
            else:
                if has_upper and has_lower and has_digit:
                    break
        strength = "Strong 💪" if length >= 12 else "Medium ⚠️" if length >= 8 else "Weak ❌"
        return (
            f"🔐 Generated Password:\n\n"
            f"  {password}\n\n"
            f"• Length: {length} characters\n"
            f"• Symbols included: {'Yes' if include_symbols else 'No'}\n"
            f"• Strength: {strength}\n\n"
            f"⚠️ Copy this now — it won't be saved anywhere!"
        )
    except Exception as e:
        return f"❌ Password generation failed: {str(e)}"


def build_agent():
    from langgraph.prebuilt import create_react_agent
    from langgraph.checkpoint.memory import MemorySaver

    llm = get_llm()

    tools = [
        search_wikipedia,
        get_current_time,
        calculate,
        get_weather,
        save_note,
        generate_password,
    ]

    system_prompt = """You are ARIA (Advanced Research & Information Assistant),
a friendly and knowledgeable personal research assistant.

Your personality:
- Warm, encouraging, and patient
- You explain things clearly without using confusing jargon
- You are enthusiastic about helping with research and learning
- You admit when you are uncertain rather than guessing

Your capabilities:
- Search Wikipedia for facts about any topic
- Check the current time and date anywhere in the world
- Perform math calculations safely
- Look up current weather conditions
- Save notes and research findings to files
- Generate secure passwords

Remember: You have memory of this whole conversation, so you can
refer back to things mentioned earlier. Be helpful, be clear, have fun!"""

    memory = MemorySaver()

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
        checkpointer=memory,
    )

    return agent


def run_agent():
    print("\n" + "=" * 55)
    print("  🤖 ARIA - Personal Research Assistant")
    print("=" * 55)
    print("Type your question and press Enter.")
    print("Type 'quit' or 'exit' to stop.")
    print("Type 'help' to see what ARIA can do.")
    print("=" * 55 + "\n")

    try:
        agent = build_agent()
    except EnvironmentError as e:
        print(e)
        return

    config = {"configurable": {"thread_id": "session_001"}}

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "bye", "goodbye"):
                print("\nARIA: Goodbye! It was great helping you today! 👋\n")
                break

            if user_input.lower() == "help":
                print("\nARIA: Here is what I can help you with:")
                print("  📖 Facts     — 'Tell me about the Eiffel Tower'")
                print("  🕐 Time      — 'What time is it in Tokyo?'")
                print("  🧮 Math      — 'What is 15% of 340?'")
                print("  🌤️ Weather   — 'What is the weather in Paris?'")
                print("  📝 Notes     — 'Save a note about Python tips'")
                print("  🔐 Passwords — 'Generate a strong password'")
                print("  💬 Just talk — I remember our whole conversation!\n")
                continue

            print("\nARIA: ", end="", flush=True)

            final_response = ""
            tools_used = []

            for chunk in agent.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config,
                stream_mode="values",
            ):
                messages = chunk.get("messages", [])
                if messages:
                    last_msg = messages[-1]
                    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                        for tc in last_msg.tool_calls:
                            name = tc.get("name", "unknown")
                            if name not in tools_used:
                                tools_used.append(name)
                                print(f"\n  🔧 [Using tool: {name}]", flush=True)
                    if hasattr(last_msg, "content") and isinstance(last_msg.content, str):
                        if last_msg.content:
                            final_response = last_msg.content

            if final_response:
                print(final_response)
            print()

        except KeyboardInterrupt:
            print("\n\nARIA: Interrupted! Type 'quit' to exit properly. 👋\n")
            break
        except Exception as e:
            print(f"\n⚠️ Something went wrong: {str(e)}")
            print("Please try again with a different question.\n")


if __name__ == "__main__":
    run_agent()