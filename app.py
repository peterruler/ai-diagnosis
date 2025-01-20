from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import openai
from dotenv import load_dotenv
import os

app = Flask(__name__, static_folder='templates')
CORS(app)

# Load environment variables
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = api_key  # Use the key from .env file

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']

    if not audio_file.filename.endswith(('.mp3', '.wav', '.m4a')):
        return jsonify({'error': 'Invalid audio file format'}), 400

    # Save and process the audio file
    audio_file.save("temp_audio.mp3")

    try:
        # Transcription
        audio_file = open("temp_audio.mp3", "rb")
        transcription = openai.Audio.transcribe(
            model="whisper-1", 
            file=audio_file,
        )
        text = transcription['text']

        # Categorization using GPT
        prompt = (f"Categorize the following text into a plain valid json object (without python multiline comments or json word) containing: firstname, familyname, age, sex, "
                    f"blood pressure, body temperature, and further vital parameters, diagnosis text with number 1.  to number 5. diagnosis:\n\n{text}")
            
        # Using the chat completion method for ChatGPT 4.0 Mini model
        response = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # Use the ChatGPT 4.0 Mini model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant specialized in medical categorization."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.5  # Adjust temperature for response creativity
            )
            
        # Extract the assistant's reply
        categories = response['choices'][0]['message']['content'].strip()
            
        return jsonify({'transcription': text, 'categories': categories})

    except Exception as e:
        return jsonify({'error': f"Error during GPT processing: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
