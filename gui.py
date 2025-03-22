import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import ttk
import yt_dlp
import moviepy.editor as mp
import speech_recognition as sr
import openai
import time
import pyttsx3
import os

openai.api_key = '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'

engine = pyttsx3.init()

engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

# Download video using yt-dlp
def download_video(url, output_path='video.mp4'):
    try:
        ydl_opts = {'outtmpl': output_path}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download video: {e}")
        return False

def extract_audio_from_video(video_path='video.mp4', audio_path='audio.wav'):
    try:
        video = mp.VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to extract audio: {e}")
        return False
def transcribe_audio(audio_path='audio.wav'):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Could not transcribe the audio."
    except sr.RequestError:
        return "Failed to connect to Google Speech Recognition."

def verify_with_openai_and_web(text):
    try:
        search_query = f"Verify this statement: {text}"
        search_results = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a fact-checking assistant that makes sure there is unnecessary steps or use previous details to recognize incorrect information in 1 sentence small bulletpoints. Dont mention about being oudated from 2023."},
                {"role": "user", "content": search_query}
            ]
        )

        search_result = search_results.choices[0].message['content']
        return search_result
    except Exception as e:
        return f"Error using OpenAI API: {e}"

def process_video():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Warning", "Please enter a valid TikTok or YouTube URL")
        return

    results_text.delete(1.0, tk.END)
    results_text.insert(tk.END, "Downloading video...\n")
    progress_bar["value"] = 10
    root.update()

    if download_video(url):
        update_progress(30)
        results_text.insert(tk.END, "Extracting audio...\n")
        if extract_audio_from_video():
            update_progress(50)
            results_text.insert(tk.END, "Transcribing audio to text...\n")
            text = transcribe_audio()
            results_text.insert(tk.END, f"Transcript: {text}\n\n")

            update_progress(70)
            results_text.insert(tk.END, "Verifying with OpenAI and Web Search...\n")
            verification_result = verify_with_openai_and_web(text)
            results_text.insert(tk.END, verification_result)

            update_progress(100)
            os.remove('video.mp4')
            os.remove('audio.wav')

            #read_aloud(f"Transcript: {text} \nVerification result: {verification_result}")

def update_progress(value):
    progress_bar["value"] = value
    root.update()
    time.sleep(0.5)

def read_aloud(text):
    engine.say(text)
    engine.runAndWait()

root = tk.Tk()
root.title("Video Fact Checker with OpenAI")
root.geometry("600x500")
root.configure(bg="#f0f0f0")

label_style = {'font': ('Arial', 12), 'bg': "#f0f0f0", 'fg': '#333'}

tk.Label(root, text="Enter TikTok or YouTube URL:", **label_style).pack(pady=10)

url_entry = tk.Entry(root, width=50, font=('Arial', 12))
url_entry.pack(pady=5)

process_button = tk.Button(root, text="Check Facts", font=('Arial', 12, 'bold'), bg='#4CAF50', fg='white', relief='raised', command=process_video)
process_button.pack(pady=15)

progress_bar = ttk.Progressbar(root, length=400, mode="determinate", maximum=100, style="TProgressbar")
progress_bar.pack(pady=10)

results_text = scrolledtext.ScrolledText(root, width=70, height=15, font=('Arial', 10), wrap=tk.WORD)
results_text.pack(pady=10)

style = ttk.Style()
style.configure("TProgressbar",
                thickness=25,
                background='#4CAF50',
                troughcolor="#f0f0f0",
                )

root.mainloop()
