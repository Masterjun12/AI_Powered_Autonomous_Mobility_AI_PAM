import vosk
import sys
import sounddevice as sd
import keyboard
import numpy as np

# Global flag to signal program exit
exit_program = False

def on_q_pressed():
    global exit_program
    exit_program = True
    print("'q' pressed. Exiting soon...")

model = vosk.Model(r"C:\Users\maste\Desktop\speech\model-ko")

samplerate = 16000
device = 1

if __name__ == "__main__":
    keyboard.add_hotkey('q', on_q_pressed) # Register hotkey for 'q'

    print("Press and hold the 'e' key to record. Release 'e' to stop.")
    print("Press 'q' to quit at any time.")

    try:
        with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16', device=device) as stream:
            while not exit_program:
                keyboard.wait('e') # Wait for 'e' key press
                if exit_program: break

                print("Recording...")
                audio_data_list = []
                while keyboard.is_pressed('e'):
                    if exit_program: break
                    data, overflowed = stream.read(1024) # Read audio in chunks
                    audio_data_list.append(data)
                print("Recording finished.")

                if exit_program: break

                if audio_data_list: # Only process if some audio was recorded
                    audio_data_np = np.concatenate(audio_data_list, axis=0)
                    audio_bytes = audio_data_np.tobytes()

                    rec = vosk.KaldiRecognizer(model, samplerate)
                    rec.AcceptWaveform(audio_bytes)
                    print(rec.FinalResult())
                else:
                    print("No audio recorded.")

    except Exception as e:
        print(f"An error occurred: {e}")

    keyboard.remove_hotkey('q') # Clean up hotkey
    print("Program exited.")