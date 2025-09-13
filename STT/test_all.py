import os
import whisper
import sounddevice as sd
import numpy as np
import keyboard
import time
import io
import wave
import speech_recognition as sr
import vosk

# Global flag to signal program exit
exit_program = False

def on_q_pressed():
    global exit_program
    exit_program = True
    print("\n'q' pressed. Exiting soon...")

# --- Configuration ---
# FFmpeg path for Whisper (based on previous debugging)
ffmpeg_bin_path = r"C:\Program Files\ffmpeg\bin"
os.add_dll_directory(ffmpeg_bin_path)
os.environ["FFMPEG_PATH"] = os.path.join(ffmpeg_bin_path, "ffmpeg.exe")

# Microphone device index
microphone_device_index = 1

samplerate = 16000 # Standard sample rate for speech recognition

# Load models once at the beginning
print("Loading Whisper model (this may take a moment)...")
whisper_model = whisper.load_model("large-v3", device="cpu")  # Use 'large-v3' for better accuracy
print("Whisper model loaded.")

print("Loading Vosk model...")
vosk_model = vosk.Model(r"C:\Users\maste\Desktop\speech\model-ko")
print("Vosk model loaded.")

# Initialize SpeechRecognition Recognizer
sr_recognizer = sr.Recognizer()

# --- Main Recording and Processing Loop ---
if __name__ == "__main__":
    keyboard.add_hotkey('q', on_q_pressed) # Register hotkey for 'q'

    print("\n--- Speech Recognition Batch Test ---")
    print("Press and hold the 'e' key to record. Release 'e' to stop.")
    print("Press 'q' to quit at any time.")

    while not exit_program:
        keyboard.wait('e') # Wait for 'e' key press
        if exit_program: break

        print("\nRecording...")
        audio_chunks = []
        try:
            with sd.InputStream(samplerate=samplerate, channels=1, dtype='float32', device=microphone_device_index) as stream:
                while keyboard.is_pressed('e'):
                    if exit_program: break
                    data, overflowed = stream.read(1024) # Read audio in chunks
                    audio_chunks.append(data)
                print("Recording finished.")

            if exit_program: break

            if not audio_chunks:
                print("No audio recorded. Try holding 'e' longer.")
                continue

            # Concatenate all recorded audio into a single NumPy array
            recorded_audio_np = np.concatenate(audio_chunks).flatten()

            print("\n--- Processing with SpeechRecognition (Google) ---")
            start_time = time.time()
            try:
                # Convert recorded numpy array to WAV bytes for SpeechRecognition
                with io.BytesIO() as wav_file:
                    with wave.open(wav_file, 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(recorded_audio_np.dtype.itemsize) # Use itemsize for float32
                        wf.setframerate(samplerate)
                        wf.writeframes((recorded_audio_np * 32767).astype(np.int16).tobytes()) # Convert to int16 for WAV
                    wav_file.seek(0)
                    audio_source = sr.AudioFile(wav_file)

                    with audio_source as source:
                        audio = sr_recognizer.record(source)

                sr_text = sr_recognizer.recognize_google(audio, language="ko-KR")
                print(f"SpeechRecognition Result: {sr_text}")
            except sr.UnknownValueError:
                print("SpeechRecognition could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
            except Exception as e:
                print(f"SpeechRecognition unexpected error: {e}")
            finally:
                end_time = time.time()
                print(f"Time taken: {end_time - start_time:.2f} seconds")

            print("\n--- Processing with Vosk ---")
            start_time = time.time()
            try:
                vosk_rec = vosk.KaldiRecognizer(vosk_model, samplerate)
                vosk_rec.AcceptWaveform(recorded_audio_np.tobytes()) # Vosk accepts raw bytes
                vosk_text = vosk_rec.FinalResult()
                print(f"Vosk Result: {vosk_text}")
            except Exception as e:
                print(f"Vosk unexpected error: {e}")
            finally:
                end_time = time.time()
                print(f"Time taken: {end_time - start_time:.2f} seconds")

            print("\n--- Processing with Whisper ---")
            start_time = time.time()
            try:
                # Whisper expects float32 numpy array, which we already have
                whisper_text = whisper_model.transcribe(recorded_audio_np, language="ko")
                print(f"Whisper Result: {whisper_text['text']}") # Corrected f-string syntax
            except Exception as e:
                print(f"Whisper unexpected error: {e}")
            finally:
                end_time = time.time()
                print(f"Time taken: {end_time - start_time:.2f} seconds")

        except Exception as e:
            print(f"An unexpected error occurred during recording or processing: {e}")

    keyboard.remove_hotkey('q') # Clean up hotkey
    print("\nProgram exited.")