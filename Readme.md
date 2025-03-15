# Personal Desktop Assistant 🤖

This is a Python-based personal desktop assistant that uses voice commands and text input to perform various tasks such as opening applications, detecting objects, and interacting with the user.

## Features

- **Voice Interaction**: Speak to the assistant using your microphone.
- **Text Commands**: Type commands directly into the interface.
- **Object Detection**: Detect objects using your webcam with YOLOv3.
- **Application Control**: Open applications like Camera, Calculator, and Music Player.
- **Web Search**: Search on Google, Wikipedia, and YouTube.
- **Screenshot**: Take screenshots and save them locally.
- **Time Query**: Ask for the current time.

## Installation

1. Clone the repository or download the project files.
2. Navigate to the project directory.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `config.py` file in the project directory to store sensitive information like API keys.
2. Add the following content to `config.py`:
   ```python
   # Configuration file to store sensitive information
   GENAI_API_KEY = "your_api_key_here"
   ```
3. Replace `"your_api_key_here"` with your actual API key.

## Usage

1. Run the application:
   ```bash
   streamlit run main.py
   ```
2. Interact with the assistant using the microphone or text input.

## File Structure

- `main.py`: The main application file.
- `config.py`: Stores sensitive information like API keys.
- `requirements.txt`: Lists all the dependencies required for the project.
- `README.md`: Documentation for the project.

## YOLOv3 Configuration

Ensure you have the following YOLOv3 files in the specified paths:
- `yolov3.cfg`: Configuration file for YOLOv3.
- `yolov3.weights`: Pre-trained weights for YOLOv3.
- `coco.names`: Class names for object detection.

Update the paths in `main.py` if your files are located elsewhere.

## Developed By

K. Srihari Sakshith  
[GitHub](https://github.com/SrihariSakshith) | [LinkedIn](https://www.linkedin.com/in/srihari-sakshith-kotichintala-1a1a8a280)
