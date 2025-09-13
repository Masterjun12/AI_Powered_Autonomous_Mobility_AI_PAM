# STT 비교분석


Notebooks: DJI GCS project (https://www.notion.so/DJI-GCS-project-2303061d2a898058ae1fd7eb5cd3af01?pvs=21)

# **STT 음성인식 라이브러리 비교 실험 보고서**

## **1. 연구 개요**

본 연구는 드론 제어 명령어 인식을 위한 STT(Speech-to-Text) 기술의 성능을 비교 분석하기 위해 수행되었습니다. 실제 드론 조종 상황에서 자주 사용되는 기본적인 명령어들을 대상으로 세 가지 주요 STT 라이브러리의 정확도와 응답성을 평가하였습니다.

## **2. 실험 대상 음성 명령어 (Task)**

실험에서는 드론 제어의 기본이 되는 다음 세 가지 명령어를 테스트하였습니다:

**Task 1: "이륙해"**

- 드론의 기본 이륙 명령어로, 단순하고 명확한 단일 동작 명령입니다.
- 이 명령어는 드론 조종에서 가장 기본적이면서도 중요한 명령으로, 정확한 인식이 필수적입니다.

**Task 2: "이륙하고 고도 10미터 유지"**

- 복합 명령어로, 이륙과 고도 유지라는 두 가지 동작을 포함합니다.
- 숫자("10미터")가 포함된 복잡한 문장 구조로, STT 시스템의 복합 명령어 처리 능력을 평가합니다.

**Task 3: "앞으로 100미터 전진"**

- 방향성과 거리를 포함한 이동 명령어입니다.
- 공간적 개념("앞으로")과 정확한 수치("100미터")를 동시에 인식해야 하는 도전적인 과제입니다.

## **3. 실험 라이브러리 분석**

### **3.1 Google Speech Recognition (speech_recognition)**

**특징:**

- 클라우드 기반 STT 서비스로, Google의 강력한 음성인식 엔진을 활용합니다.
- 다양한 언어를 지원하며, 특히 한국어 인식에서 높은 정확도를 보입니다.
- 인터넷 연결이 필수적이며, 실시간 처리보다는 배치 처리에 최적화되어 있습니다.

**기술적 구현:**

- sounddevice를 통해 실시간 오디오 스트림을 캡처합니다.
- numpy 배열로 수집된 오디오 데이터를 WAV 형식으로 변환하여 처리합니다.
- 16kHz 샘플링 레이트로 모노 채널 오디오를 사용합니다.

**장단점:**

- 장점: 높은 인식 정확도, 다양한 언어 지원, 노이즈 제거 능력
- 단점: 인터넷 연결 필수, 클라우드 의존성, 개인정보 보안 이슈

### **3.2 Vosk (오프라인 음성인식)**

**특징:**

- 완전한 오프라인 기반 STT 라이브러리로, 로컬 환경에서 독립적으로 동작합니다.
- Kaldi 음성인식 엔진을 기반으로 하며, 실시간 스트리밍 처리에 최적화되어 있습니다.
- 사전 훈련된 언어 모델을 로컬에 저장하여 사용합니다.

**기술적 구현:**

- KaldiRecognizer를 사용하여 실시간 오디오 스트림을 처리합니다.
- AcceptWaveform 메서드를 통해 오디오 청크를 순차적으로 처리합니다.
- 로컬 한국어 모델(model-ko)을 사용하여 인식을 수행합니다.

**장단점:**

- 장점: 완전한 오프라인 동작, 빠른 응답 시간, 개인정보 보안 우수
- 단점: 모델 크기가 큰 편, 클라우드 서비스 대비 상대적으로 낮은 정확도

### **3.3 OpenAI Whisper**

**특징:**

- OpenAI에서 개발한 최신 딥러닝 기반 STT 모델입니다.
- 다양한 크기의 모델을 제공하며, 본 실험에서는 large-v3 모델을 사용했습니다.
- 로컬 환경에서 동작하지만 GPU 가속을 통해 성능을 향상시킬 수 있습니다.

**기술적 구현:**

- float32 형식의 오디오 데이터를 직접 처리합니다.
- FFmpeg를 통한 오디오 전처리를 수행합니다.
- CPU 모드로 동작하도록 설정하여 하드웨어 호환성을 확보했습니다.

**장단점:**

- 장점: 최신 딥러닝 기술, 높은 정확도, 다양한 모델 크기 선택 가능
- 단점: 높은 컴퓨팅 리소스 요구, 상대적으로 느린 처리 속도

## **4. 실험 코드**

### **4.1 Google Speech Recognition 구현**

python

```jsx
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
```

### **4.2 Vosk 구현**

python

```
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
```

### **4.3 OpenAI Whisper 구현**

python

```python
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
```

## **5. 실험 결과**

### **5.1 Google Speech Recognition**

- 가장 기본적인 방식

![그림01.jpg](%EA%B7%B8%EB%A6%BC01.jpg)

정해 놓은 시퀀스 길이에 따라 끝에 말이 잘리는 현상이 발생 > 40초로 변경 후 높은 인식률을 보임

- 사운드 드라이브 전처리후 삽입 방식

![그림05.jpg](%EA%B7%B8%EB%A6%BC05.jpg)

사운드 드라이브에서 음성을 받아서 그 후 전송하는 방식으로 변경함

기본 모델에 바로 입력하는 것보다 개선된 인식률, 처리까지의 시간은 조금 증가함

### **5.2 Vosk**

- 한국어 기본 모델

![그림02.jpg](%EA%B7%B8%EB%A6%BC02.jpg)

3개 중 가장 나쁜 인식률을 보여주었음. 한국어 모델의 학습력이 부족한 것으로 보임

### **5.3 OpenAI Whisper**

- Base 모델 실험

![그림03.jpg](%EA%B7%B8%EB%A6%BC03.jpg)

Base 모델 답게 Vosk 와 비슷한 인식 수준을 보여줌 이는 추후 Large 모델과의 차이가 극명하게 나타남

![그림04.jpg](%EA%B7%B8%EB%A6%BC04.jpg)

- Large -V3 모델 실험결과, 높은 인식률을 보여주고 있음, 단점은 시간이 오래걸림
- 하지만 단점은 음성이 녹음 된 후 결과출력까지 20초 가량의 시간이 소요되는 점

![그림06.jpg](%EA%B7%B8%EB%A6%BC06.jpg)

## **6. 결론 및 향후 연구 방향**

본 연구를 통해 드론 제어 명령어 인식을 위한 STT 라이브러리들의 특성과 성능을 비교 분석하였습니다. 각 라이브러리는 고유한 장단점을 가지고 있으며, 실제 드론 제어 시스템에 적용할 때는 정확도, 응답 시간, 네트워크 의존성, 보안성 등을 종합적으로 고려해야 합니다.

향후 연구에서는 더 다양한 드론 명령어와 환경적 요인(소음, 거리 등)을 고려한 확장된 실험을 통해 각 STT 시스템의 실용성을 더욱 정확히 평가할 필요가 있습니다.

---
