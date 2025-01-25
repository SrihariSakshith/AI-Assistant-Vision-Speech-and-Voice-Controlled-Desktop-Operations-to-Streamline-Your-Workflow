import datetime
import cv2
import win32com.client
import speech_recognition as sr
from django.templatetags.i18n import language
import webbrowser
import pyautogui
import google.generativeai as genai
import os

speaker = win32com.client.Dispatch("SAPI.SpVoice")

def say(text):
    if text[:3] == "AI:":
        text=text[3:]
    print("AI: "+text)
    speaker.Speak(f"{text}")

def takeCommand():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        audio = r.listen(source)
        try:
            query = r.recognize_google(audio,language="en-in")
            print(f"You: {query}")
            return str(query)
        except Exception as e:
            say("Sorry can you repeat.")
            return "Sorry can you repeat."

if __name__=="__main__":
    current_hour = datetime.datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Good morning, Sir!"
    elif 12 <= current_hour < 18:
        greeting = "Good afternoon, Sir!"
    elif 18 <= current_hour < 22:
        greeting = "Good evening, Sir!"
    else:
        greeting = "Hello, Sir!"
    say(greeting)
    chat = "You: You are my personal assisstant, your answers will be converted to speech so answer accordingly. Talk as a person.\n AI: Ok\n"

    while True:
        print("Listening......")
        query = takeCommand()
        if "go offline" in query.lower():
            break
        chat += "You: "+query+"\n"
        sites = [["youtube","https://www.youtube.com"],["wikipedia","https://www.youtube.com"],["google","https://www.google.com"]]
        f=0
        for site in sites:
            if f"Open {site[0]}".lower() in query.lower():
                say(f"Opening {site[0]} sir...")
                webbrowser.open(site[1])
                f=1
                chat+=f"AI: site is opened\n"
        if f==1:
            continue
        elif "open music" in query.lower():
            musicPath = r"C:\Users\91944\Downloads\karthikeya_2_flute_bgm.mp3"
            os.startfile(musicPath)
            chat += f"AI: Music is played.\n"
        elif "the time" in query.lower():
            hour = datetime.datetime.now().strftime("%H")
            min = datetime.datetime.now().strftime("%M")
            say(f"Sir the time is {hour} hours {min} minutes.")
            chat += f"AI: Sir the time is {hour} hours {min} minutes.\n"
        elif "Open Camera".lower() in query.lower():
            try:
                say("Opening Camera")
                os.system("start microsoft.windows.camera:")
                chat += "AI: Opened Camera\n"
            except Exception as e:
                say(f"Failed to open Camera. Error: {e}")
                chat += f"AI: Failed to open Camera. Error: {e}.\n"
        elif "Open Calculator".lower() in query.lower():
            try:
                say("Opening Calculator")
                os.system("start calculator:")
                chat += "AI: Opened Calculator\n"
            except Exception as e:
                say(f"Failed to open Calculator. Error: {e}")
                chat += f"AI: Failed to open Calculator. Error: {e}.\n"
        elif "Take Screenshot".lower() in query.lower():
            screenshot = pyautogui.screenshot()
            # Save the screenshot to the specified file
            say("Taking Screenshot.")
            screenshot.save(r"C:\Users\91944\Downloads\photo.jpg")
            chat += "AI: Took Screenshot\n"
        else:
            genai.configure(api_key="AIzaSyAUiaFtrGFNdflaMPV1h6-7gt63xBSn3ac")
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(chat)
            chat += "AI: " + str(response.text) + "\n"
            say(str(response.text))
