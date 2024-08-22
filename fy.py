import speech_recognition as sr
from googletrans import Translator
from twilio.rest import Client
import geocoder
import tkinter as tk
from tkinter import scrolledtext
import threading

# Initialize recognizer and translator
recognizer = sr.Recognizer()
translator = Translator()

# Twilio credentials
account_sid = 'AC4d10cc17317a6661ebf2f6145d0670a9'
auth_token = 'f315c2615a5253df890135b110a9c54a'
twilio_number = '+18154539583'
client = Client(account_sid, auth_token)

def translate_text(text, target_language='en'):
    translation = translator.translate(text, dest=target_language)
    return translation.text

def send_sms_twilio(to_number, message_body):
    message = client.messages.create(
        body=message_body,
        from_=twilio_number,
        to=to_number
    )
    return message.sid

def get_gps_location():
    g = geocoder.ip('me')
    return g.latlng

def update_ui(message, is_special=False):
    if is_special:
        special_message_label.config(text=message)
        special_message_label.pack(pady=20)
        text_area.pack_forget()
    else:
        special_message_label.pack_forget()
        text_area.insert(tk.END, message + "\n")
        text_area.yview(tk.END)

def recognition_thread():
    update_ui("Listening for speech...")

    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio, language='sw')
            update_ui(f"Recognized text: {text}")

            translated_text = translate_text(text, target_language='en')
            update_ui(f"Translated text: {translated_text}")

            location = get_gps_location()
            location_text = f"GPS Coordinates: {location[0]}, {location[1]}"
            update_ui(f"Location: {location_text}")

            message_body = f"{translated_text}\n{location_text}"
            sid = send_sms_twilio('+919940625457', message_body)
            update_ui(f"Message sent with SID: {sid}")

        except Exception as e:
            update_ui(f"An error occurred: {e}")

# GUI setup
root = tk.Tk()
root.title("Speech Recognition and SMS Sender")
root.geometry("700x600")
root.configure(bg='#D0F0C0')

frame = tk.Frame(root, bg='#F5F5DC', padx=15, pady=15)
frame.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)

title_label = tk.Label(frame, text="Speech Recognition and SMS Sender", font=("Arial", 18, "bold"), bg='#F5F5DC', fg='#4B0082')
title_label.pack(pady=10)

text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20, width=80, bg='#FAFAD2', font=("Arial", 12))
text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

special_message_label = tk.Label(frame, text="", font=("Arial", 24, "bold"), bg='#F5F5DC', fg='#FF0000')

start_button = tk.Button(frame, text="Start Recognition", font=("Arial", 14), bg='#32CD32', fg='white', relief=tk.RAISED, command=lambda: threading.Thread(target=recognition_thread, daemon=True).start())
start_button.pack(pady=10)

exit_button = tk.Button(frame, text="Exit", font=("Arial", 14), bg='#FF4500', fg='white', relief=tk.RAISED, command=root.quit)
exit_button.pack(pady=10)

root.mainloop()

