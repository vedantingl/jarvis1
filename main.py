import speech_recognition as sr
import pyttsx3
import requests
import json
import re
import os
import subprocess
import webbrowser

# CONFIGURATION
API_KEY = "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"  # Replace this with your real key
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://your-site-or-project.com",  # Put your GitHub repo or site
    "X-Title": "Jarvis Assistant"
}

# TEXT-TO-SPEECH
engine = pyttsx3.init()
engine.setProperty("rate", 180)

# SPEECH RECOGNITION
recognizer = sr.Recognizer()
microphone = sr.Microphone()

def speak(text):
    print("🗣️ Jarvis:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎤 Listening...")
        audio = recognizer.listen(source)
    try:
        print("🔍 Recognizing...")
        query = recognizer.recognize_google(audio)
        print("🗣️ You said:", query)
        return query
    except sr.UnknownValueError:
        print("⚠️ Couldn't understand audio.")
        return None
    except sr.RequestError as e:
        print("❌ Could not request results; {0}".format(e))
        return None

def clean_response(text):
    text = re.sub(r'\\n|\n|\r', ' ', text)
    text = re.sub(r'[*_#>\[\]{}|]', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def chat_with_deepseek(prompt):
    try:
        data = {
            "model": "deepseek/deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are Jarvis, an intelligent AI assistant."},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(API_URL, headers=HEADERS, data=json.dumps(data))
        if response.status_code == 200:
            result = response.json()
            message = result["choices"][0]["message"]["content"]
            print("🧠 AI Response:", message)
            return clean_response(message)
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return "Sorry, I couldn't get a response from the AI."
    except Exception as e:
        print("❌ Exception:", str(e))
        return "There was a problem connecting to the AI."

# SYSTEM COMMANDS
def shutdown():
    speak("Shutting down the system.")
    os.system("shutdown /s /t 1")

def open_chrome():
    speak("Opening Chrome.")
    path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    subprocess.Popen([path])

def search_google(query):
    speak(f"Searching Google for {query}")
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)

def open_folder(folder_name):
    speak(f"Opening folder {folder_name}")
    base_path = os.path.expanduser("~")  # User home directory
    folder_path = os.path.join(base_path, folder_name)
    if os.path.exists(folder_path):
        os.startfile(folder_path)
    else:
        speak("Sorry, I can't find that folder.")

# MAIN LOOP
if __name__ == "__main__":
    speak("Hello, I am Jarvis. Say 'Jarvis' to activate me.")

    while True:
        print("🕒 Waiting for wake word 'Jarvis'...")
        wake_input = listen()

        if wake_input and "jarvis" in wake_input.lower():
            speak("Yes? What would you like me to do?")
            command = listen()

            if command:
                command_lower = command.lower()

                if any(word in command_lower for word in ["exit", "quit", "stop", "bye"]):
                    speak("Goodbye! Have a great day.")
                    break

                elif "shutdown" in command_lower:
                    shutdown()
                    break

                elif "open chrome" in command_lower:
                    open_chrome()

                elif "search for" in command_lower or "google" in command_lower:
                    search_query = command_lower.replace("search for", "").replace("google", "").strip()
                    if search_query:
                        search_google(search_query)
                    else:
                        speak("What should I search for?")

                elif "open folder" in command_lower:
                    folder = command_lower.replace("open folder", "").strip()
                    open_folder(folder)

                else:
                    response = chat_with_deepseek(command)
                    speak(response)
            else:
                speak("Sorry, I didn't catch that.")
