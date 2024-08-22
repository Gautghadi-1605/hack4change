import os
import wave
import pyaudio
import pyttsx3
from faster_whisper import WhisperModel

# Define constants
NEON_GREEN = '\033[32m'
RESET_COLOR = '\033[0m'

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Initialize text-to-speech engine
tts = pyttsx3.init()

# Helpline database (for simulation purposes)
helpline_database = {
    "fire": '+919940625457',  # Simulated number
    "police": '+919940625457'  # Simulated number
}

def find_helpline_number(keyword):
    return helpline_database.get(keyword.lower(), None)

def record_chunk(p, stream, file_path, chunk_length=10):
    frames = []
    print("Recording...")
    for _ in range(0, int(16000 / 1024 * chunk_length)):
        data = stream.read(1024)
        frames.append(data)

    print("Finished recording.")
    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))

def transcribe_chunk(model, file_path):
    print(f"Transcribing: {file_path}")
    segments, info = model.transcribe(file_path, beam_size=7)
    transcription = ''.join(segment.text for segment in segments)
    return transcription

def map_words(transcription):
    word_map = {
        "मोटो": "fire",
        "पोलीसी": "police",
        "moto" :"fire",
        "Policía":"police"
    
    }
    
    words = transcription.lower().split()
    mapped_words = [word_map.get(word, word) for word in words]
    return ' '.join(mapped_words)

def make_call(mapped_transcription):
    helpline_number = find_helpline_number(mapped_transcription)
    if helpline_number:
        message = f"Calling {mapped_transcription} helpline number {helpline_number}"
        print(NEON_GREEN + message + RESET_COLOR)
        tts.say(message)
        tts.runAndWait()
    else:
        message = "No matching helpline found"
        print(NEON_GREEN + message + RESET_COLOR)
        tts.say(message)
        tts.runAndWait()

def main2():
    model = WhisperModel("medium", device="cpu")

    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)

    accumulated_transcription = ""

    try:
        while True:
            chunk_file = "temp_chunk.wav"
            record_chunk(p, stream, chunk_file)

            transcription = transcribe_chunk(model, chunk_file)
            print(NEON_GREEN + transcription + RESET_COLOR)

            # Map transcribed words
            mapped_transcription = map_words(transcription)

            # Process if the mapped transcription is meaningful
            if mapped_transcription in helpline_database:
                make_call(mapped_transcription)
            else:
                print("No action required for the transcription.")

            os.remove(chunk_file)
            accumulated_transcription += transcription + " "

    except KeyboardInterrupt:
        print("Stopping...")

        with open("log.txt", "w") as log_file:
            log_file.write(accumulated_transcription)

    finally:
        print("LOG: " + accumulated_transcription)
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main2()

