import speech_recognition as sr
import keyboard
import sounddevice as sd
import numpy as np
import io
import wave

# Global flag to signal program exit
exit_program = False

def recognize_speech():
    global exit_program
    r = sr.Recognizer()
    samplerate = 16000  # Standard sample rate for speech recognition

    print("Press and hold the 'e' key to record. Release 'e' to stop.")
    print("Press 'q' to quit at any time.")

    keyboard.wait('e') # Wait for 'e' key press
    if exit_program: return

    print("Recording...")
    audio_data_list = []
    try:
        with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16') as stream:
            while keyboard.is_pressed('e'):
                if exit_program: break
                data, overflowed = stream.read(1024) # Read audio in chunks
                audio_data_list.append(data)
            print("Recording finished.")

        if exit_program: return

        # Convert recorded numpy array to bytes for SpeechRecognition
        audio_data_np = np.concatenate(audio_data_list, axis=0)
        audio_bytes = audio_data_np.tobytes()

        # Create a WAV file in memory
        with io.BytesIO() as wav_file:
            with wave.open(wav_file, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(audio_data_np.dtype.itemsize)
                wf.setframerate(samplerate)
                wf.writeframes(audio_bytes)
            wav_file.seek(0)
            audio_source = sr.AudioFile(wav_file)

            with audio_source as source:
                audio = r.record(source)

        print("Processing speech...")
        text = r.recognize_google(audio, language="ko-KR")
        print("Google Speech Recognition thinks you said: " + text)

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def on_q_pressed():
    global exit_program
    exit_program = True
    print("'q' pressed. Exiting soon...")

if __name__ == "__main__":
    keyboard.add_hotkey('q', on_q_pressed) # Register hotkey for 'q'

    while not exit_program:
        recognize_speech()

    keyboard.remove_hotkey('q') # Clean up hotkey
    print("Program exited.")