import streamlit as st
import datetime
import os
import pyautogui
import webbrowser
import speech_recognition as sr
import win32com.client
import google.generativeai as genai
import pythoncom  # Import pythoncom
import cv2
from gtts import gTTS
from playsound import playsound
from config import GENAI_API_KEY  # Import the API key from config.py

pythoncom.CoInitialize()  # Initialize COM library

speaker = win32com.client.Dispatch("SAPI.SpVoice")

def say(text):
    # Avoid repeating "AI:" if it already exists
    if text.startswith("AI:"):
        text = text[3:].strip()
    st.write("AI: " + text)
    speaker.Speak(f"{text}")

def takeCommand():
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.pause_threshold = 1
            audio = r.listen(source)
            try:
                query = r.recognize_google(audio, language="en-in")
                st.write(f"You: {query}")
                return str(query)
            except Exception:
                return "wait"  # Return "wait" without calling say here
    except AttributeError:
        return "microphone_error"  # Return a specific error code for microphone issues

# YOLO file paths (update with your actual paths if different)
YOLO_CFG_PATH = r"C:\Users\91944\Downloads\yolov3.cfg"
YOLO_WEIGHTS_PATH = r"C:\Users\91944\Downloads\yolov3.weights"
YOLO_CLASSES_PATH = r"C:\Users\91944\Downloads\coco.names"

def load_yolo_model(cfg_path, weights_path, classes_path):
    net = cv2.dnn.readNet(weights_path, cfg_path)
    with open(classes_path, "r") as f:
        classes = [line.strip() for line in f.readlines()]
    return net, classes

def detect_objects(image, net, classes):
    height, width = image.shape[:2]
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    layer_outputs = net.forward(output_layers)
    boxes, confidences, class_ids = [], [], []
    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = int(scores.argmax())
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x, center_y, box_width, box_height = (detection[:4] * [width, height, width, height]).astype("int")
                x = int(center_x - box_width / 2)
                y = int(center_y - box_height / 2)
                boxes.append([x, y, int(box_width), int(box_height)])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    results = []
    if len(indices) > 0:  # Check if indices is not empty
        for i in indices.flatten():
            x, y, w, h = boxes[i]
            results.append((classes[class_ids[i]], confidences[i], (x, y, w, h)))
    return results

def draw_boxes(image, detections):
    for label, confidence, box in detections:
        x, y, w, h = box
        color = (0, 255, 0)
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        cv2.putText(image, f"{label} {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return image

def speech(text):
    print(text)
    language = "en"
    output = gTTS(text=text, lang=language, slow=False)
    if not os.path.exists("./sounds"):
        os.makedirs("./sounds")
    output_path = "./sounds/output.mp3"
    output.save(output_path)
    playsound(output_path)

detected_objects_global = []  # Global variable to store detected objects

def detect_objects_in_camera(chat):
    global detected_objects_global
    net, classes = load_yolo_model(YOLO_CFG_PATH, YOLO_WEIGHTS_PATH, YOLO_CLASSES_PATH)
    video = cv2.VideoCapture(0)
    detected_labels = []
    while True:
        ret, frame = video.read()
        if not ret:
            say("Failed to capture video.")
            break
        detections = detect_objects(frame, net, classes)
        for label, _, _ in detections:
            if label not in detected_labels:
                detected_labels.append(label)
        frame_with_boxes = draw_boxes(frame, detections)
        cv2.imshow("YOLO Object Detection", frame_with_boxes)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    video.release()
    cv2.destroyAllWindows()
    detected_objects_global = detected_labels  # Store detected objects globally
    if detected_labels:
        speech_text = "I detected the following objects: " + ", ".join(detected_labels) + "."
        chat += f"AI: Detected objects: {', '.join(detected_labels)}.\n"
    else:
        speech_text = "No objects were detected."
        chat += "AI: No objects were detected.\n"
    speech(speech_text)
    return chat

def answerCommand(query, chat):
    global detected_objects_global
    # Remove "Command!" prefix and clean up the query
    query = query.lower().replace("command!", "").strip()
    
    if "go offline" in query:
        say("Going Offline sir.")
        exit()
    sites = [["youtube", "https://www.youtube.com"], ["wikipedia", "https://www.wikipedia.org"], ["google", "https://www.google.com"]]
    f = 0
    for site in sites:
        if f"open {site[0]}" in query:
            say(f"Opening {site[0]} sir...")
            webbrowser.open(site[1])
            f = 1
            chat += f"AI: {site[0]} is opened\n"
            break  # Prevent duplicate responses
    if f == 1:
        return chat
    elif "search" in query and "google" in query:
        search_query = query.replace("search", "").replace("in google", "").strip()
        say(f"Searching for {search_query} in Google...")
        webbrowser.open(f"https://www.google.com/search?q={search_query}")
        chat += f"AI: Searched for {search_query} in Google.\n"
    elif "search" in query and "wikipedia" in query:
        search_query = query.replace("search", "").replace("in wikipedia", "").strip()
        say(f"Searching for {search_query} in Wikipedia...")
        webbrowser.open(f"https://en.wikipedia.org/wiki/{search_query.replace(' ', '_')}")
        chat += f"AI: Searched for {search_query} in Wikipedia.\n"
    elif "search" in query and "youtube" in query:
        search_query = query.replace("search", "").replace("in youtube", "").strip()
        say(f"Searching for {search_query} in YouTube...")
        webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
        chat += f"AI: Searched for {search_query} in YouTube.\n"
    elif "open music" in query:
        musicPath = r"C:\Users\91944\Downloads\karthikeya_2_flute_bgm.mp3"
        os.startfile(musicPath)
        chat += f"AI: Music is played.\n"
    elif "the time" in query:
        hour = datetime.datetime.now().strftime("%H")
        min = datetime.datetime.now().strftime("%M")
        say(f"Sir the time is {hour} hours {min} minutes.")
        chat += f"AI: Sir the time is {hour} hours {min} minutes.\n"
    elif "open camera" in query:
        try:
            say("Opening Camera")
            os.system("start microsoft.windows.camera:")
            chat += "AI: Opened Camera\n"
        except Exception as e:
            say(f"Failed to open Camera. Error: {e}")
            chat += f"AI: Failed to open Camera. Error: {e}.\n"
    elif "open calculator" in query:
        try:
            say("Opening Calculator")
            os.system("start calculator:")
            chat += "AI: Opened Calculator\n"
        except Exception as e:
            say(f"Failed to open Calculator. Error: {e}")
            chat += f"AI: Failed to open Calculator. Error: {e}.\n"
    elif "take screenshot" in query:
        screenshot = pyautogui.screenshot()
        say("Taking Screenshot.")
        screenshot.save(r"C:\Users\91944\Downloads\photo.jpg")
        chat += "AI: Took Screenshot\n"
    elif "detect objects" in query or "see objects" in query or "what is in front of camera" in query:
        say("Detecting objects in front of the camera.")
        chat = detect_objects_in_camera(chat)  # Pass chat to store detected objects
    elif "what objects detected" in query:
        if detected_objects_global:
            detected_objects_text = ", ".join(detected_objects_global)
            say(f"I detected the following objects: {detected_objects_text}. Do you want me to provide more detail on a specific object?")
            chat += f"AI: I detected the following objects: {detected_objects_text}. Do you want me to provide more detail on a specific object?\n"
        else:
            say("I have not detected any objects yet. Please try detecting objects first.")
            chat += "AI: I have not detected any objects yet. Please try detecting objects first.\n"
    else:
        chat += f"AI: {query}\n"
    return chat

def main():
    global conversation_log  # Declare global variable at the start of the function

    # Persistent conversation log
    if "conversation_log" not in st.session_state:
        st.session_state.conversation_log = []  # Initialize session state for conversation log
    conversation_log = st.session_state.conversation_log  # Assign session state to global variable

    st.set_page_config(page_title="Personal AI Assistant", page_icon="🤖", layout="wide")
    st.title("🤖 Personal Desktop Assistant")
    st.write("Interact with your assistant using the microphone or text input below.")

    # Sidebar for additional options
    with st.sidebar:
        st.header("Assistant Settings")
        st.write("Customize your assistant:")
        st.text("Voice: Enabled")
        st.text("Language: English")
        st.markdown("---")

        # Chat history display in the sidebar
        if st.button("Get History"):
            st.subheader("Chat History")
            if conversation_log:
                st.write("<br>".join(conversation_log).replace("\n", "<br>"), unsafe_allow_html=True)
            else:
                st.write("No history available.")

        st.markdown("---")
        st.write("Developed by: K.Srihari Sakshith")
        st.markdown("[GitHub](https://github.com/SrihariSakshith) | [LinkedIn](www.linkedin.com/in/srihari-sakshith-kotichintala-1a1a8a280)")
        st.markdown("---")

    # Initial context (hidden from displayed chat history)
    initial_context = (
        "AI: Hello! I am your personal desktop assistant. How can I help you today?\n"
        "You: You are my personal desktop assistant. You need to follow below rules: "
        "If I say something in my conversation which means open camera then you should answer as command! Open Camera, "
        "if it means open calculator your answer should be command! Open Calculator, "
        "if it means something related to take screenshot your answer should be Command! Take ScreenShot, "
        "if it means something related to shut down or go offline your answer should be Command! Go Offline, "
        "if it means something related to opening YouTube, Wikipedia, or Google, your answer should be Command! Open <site>, "
        "if it means playing music your answer should be Command! Open Music, "
        "if it means searching or opening for something in Google, Wikipedia, or YouTube, your answer should be Command! Search <query> in <platform>, "
        "if it means detecting objects in front of the camera or seeing objects, your answer should be Command! Detect Objects. "
        "If my command is none of them then you should give your response. It should go as a normal conversation. "
        "Your answers are directly converted to conversation without making any changes.\n"
        "AI: Ok\n"
    )

    # User input section
    st.subheader("Your Input")
    col1, col2 = st.columns([1, 3])
    with col1:
        mic_button = st.button("🎤 Use Microphone")
    with col2:
        query = st.text_input("Type your command here:")

    if mic_button:
        query = takeCommand()
        if query == "wait":
            say("Sorry, can you repeat?")
        elif query == "microphone_error":
            say("Microphone access is unavailable. Please check PyAudio installation.")
        else:
            conversation_log.append(f"You: {query}")
            # Configure genai with the API key from config.py
            genai.configure(api_key=GENAI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(initial_context + "\n".join(conversation_log))
            reply = str(response.text).strip()
            reply = reply.replace("AI: ", "").strip()  # Clean redundant "AI:" prefixes
            reply = reply.replace("Searched for", "").strip()  # Remove redundant "Searched for" text
            conversation_log.append(f"AI: {reply}")
            say(reply)  # Output the AI's reply
            # Check if the AI's reply contains a valid command
            if "command!" in reply.lower():  # Only pass to answerCommand if it contains a valid command
                updated_chat = answerCommand(reply, "\n".join(conversation_log))
                if updated_chat:  # If the command was handled, update the conversation log
                    conversation_log = updated_chat.split("\n")
            st.session_state.conversation_log = conversation_log  # Update session state
    elif query:  # Handle text input
        conversation_log.append(f"You: {query}")
        # Configure genai with the API key from config.py
        genai.configure(api_key=GENAI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(initial_context + "\n".join(conversation_log))
        reply = str(response.text).strip()
        reply = reply.replace("AI: ", "").strip()  # Clean redundant "AI:" prefixes
        reply = reply.replace("Searched for", "").strip()  # Remove redundant "Searched for" text
        conversation_log.append(f"AI: {reply}")
        say(reply)  # Output the AI's reply
        # Check if the AI's reply contains a valid command
        if "command!" in reply.lower():  # Only pass to answerCommand if it contains a valid command
            updated_chat = answerCommand(reply, "\n".join(conversation_log))
            if updated_chat:  # If the command was handled, update the conversation log
                conversation_log = updated_chat.split("\n")
        st.session_state.conversation_log = conversation_log  # Update session state

if __name__ == "__main__":
    main()