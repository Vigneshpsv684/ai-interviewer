
import speech_recognition as sr
import sounddevice as sd


def listen():

    recognizer = sr.Recognizer()

    print("\n🎤 Listening...")

    sample_rate = 16000
    duration = 15

    # Laptop microphone
    device_id = 1

    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
        device=device_id
    )

    sd.wait()

    audio_data = recording.tobytes()

    audio = sr.AudioData(
        audio_data,
        sample_rate,
        2
    )

    try:

        print("Converting speech to text...")

        text = recognizer.recognize_google(audio)

        return text

    except sr.UnknownValueError:

        print("Sorry, I could not understand your answer.")
        return ""

    except sr.RequestError:

        print("Speech recognition service is unavailable.")
        return ""