import os
import whisper
import sounddevice as sd
import numpy as np
import keyboard
import subprocess

# Global flag to signal program exit
exit_program = False

def on_q_pressed():
    global exit_program
    exit_program = True
    print("'q' pressed. Exiting soon...")

# Add ffmpeg bin directory to DLL search path for whisper
# NOTE: This path should point to the 'bin' directory of your ffmpeg installation.
# Based on previous 'where ffmpeg' output, it's C:\Program Files\ffmpeg\bin
# If you manually installed ffmpeg elsewhere, update this path accordingly.
ffmpeg_bin_path = r"C:\Program Files\ffmpeg\bin"
os.add_dll_directory(ffmpeg_bin_path)

# Set the FFMPEG_PATH environment variable for whisper
# This should point to the ffmpeg.exe executable.
ffmpeg_exe_path = os.path.join(ffmpeg_bin_path, "ffmpeg.exe")
os.environ["FFMPEG_PATH"] = ffmpeg_exe_path

# --- Debugging Code Start ---
print("--- FFmpeg Debugging Info ---")
print(f"FFMPEG_PATH environment variable set to: {os.environ.get('FFMPEG_PATH')}")  

if os.path.exists(ffmpeg_exe_path):
    print(f"ffmpeg.exe found at: {ffmpeg_exe_path}")
    try:
        # Test if ffmpeg can be executed from Python
        result = subprocess.run([ffmpeg_exe_path, "-version"], capture_output=True, text=True, check=True)
        print("FFmpeg -version output (from Python):")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg -version: {e}")
        print(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        print(f"Error: ffmpeg.exe not found at {ffmpeg_exe_path} (even though os.path.exists returned True).")
else:
    print(f"Error: ffmpeg.exe NOT found at the specified path: {ffmpeg_exe_path}")
print("---------------------------")
# --- Debugging Code End ---

model = whisper.load_model("large-v3", device="cpu")  # Load the Whisper model

def record_audio(samplerate=16000, device=1):
    global exit_program
    print("Press and hold the 'e' key to record. Release 'e' to stop.")
    print("Press 'q' to quit at any time.")

    keyboard.wait('e') # Wait for 'e' key press
    if exit_program: return np.array([])

    print("Recording...")
    audio_chunks = []
    try:
        with sd.InputStream(samplerate=samplerate, channels=1, dtype='float32', device=device) as stream:
            while keyboard.is_pressed('e'):
                if exit_program: break
                data, overflowed = stream.read(1024) # Read audio in chunks
                audio_chunks.append(data)
            print("Recording finished.")

        if exit_program: return np.array([])

        return np.concatenate(audio_chunks).flatten()

    except Exception as e:
        print(f"An unexpected error occurred during recording: {e}")
        return np.array([])

def main():
    global exit_program
    keyboard.add_hotkey('q', on_q_pressed) # Register hotkey for 'q'

    while not exit_program:
        audio_data = record_audio()
        if audio_data.size > 0:
            try:
                result = model.transcribe(audio_data, language="ko")
                print("Whisper thinks you said: " + result["text"])
            except Exception as e:
                print(f"An error occurred during transcription: {e}")

    keyboard.remove_hotkey('q') # Clean up hotkey
    print("Program exited.")

if __name__ == "__main__":
    main()