import abc
import time
import functools
import sounddevice as sd
import wave
import os
from datetime import datetime
import assemblyai as aai
from elevenlabs import play
from elevenlabs.client import ElevenLabs
from modules.simple_llm import build_mini_model, prompt
import threading
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


fs = 44100  # Sample rate
channels = 1  # Mono audio
duration = 15


class PersonalAssistantFramework(abc.ABC):
    @staticmethod
    def timeit_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(
                f"⏰ {args[0].__class__.__name__} - {func.__name__}() took {end_time - start_time:.2f} seconds"
            )
            return result

        return wrapper

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def transcribe(self, file_path):
        pass

    @abc.abstractmethod
    def speak(self, text: str):
        pass

    @abc.abstractmethod
    def think(self, prompt: str) -> str:
        pass


class AssElevenPAF(PersonalAssistantFramework):
    def setup(self):
        aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
        self.elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVEN_API_KEY"))
        self.llm_model = build_mini_model()

    @PersonalAssistantFramework.timeit_decorator
    def generate_voice_audio(self, text: str):
        audio = self.elevenlabs_client.generate(
            text=text,
            voice="WejK3H1m7MI9CHnIjW9K",
            model="eleven_turbo_v2",
        )

        return audio

    @PersonalAssistantFramework.timeit_decorator
    def transcribe(self, file_path):
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(file_path)
        return transcript.text

    def speak(self, text: str):
        audio = self.generate_voice_audio(text)
        play(audio)

    @PersonalAssistantFramework.timeit_decorator
    def think(self, thought: str) -> str:
        return prompt(self.llm_model, thought)


class OpenPAF(PersonalAssistantFramework):
    def setup(self):
        pass

    def transcribe(self, file_path):
        pass

    def speak(self, text: str):
        pass

    def think(self, prompt: str) -> str:
        pass


class RoqPAF(PersonalAssistantFramework):
    def setup(self):
        pass

    def transcribe(self, file_path):
        pass

    def speak(self, text: str):
        pass

    def think(self, prompt: str) -> str:
        pass


def record_audio(duration=duration, fs=fs, channels=channels):
    """Record audio from the microphone."""

    print("🔴 Recording...")
    recording = sd.rec(
        int(duration * fs), samplerate=fs, channels=channels, dtype="int16"
    )

    def duration_warning():
        time.sleep(duration)
        if not stop_event.is_set():
            print(
                "⚠️ Record limit hit - your assistant won't hear what you're saying now. Increase the duration."
            )

    stop_event = threading.Event()
    warning_thread = threading.Thread(target=duration_warning)
    warning_thread.daemon = (
        True  # Set the thread as daemon so it doesn't block program exit
    )
    warning_thread.start()

    input("🟡 Press Enter to stop recording...")
    stop_event.set()
    sd.stop()

    print(f"🍞 Recording Chunk Complete")
    return recording


def create_audio_file(recording):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"audio_{timestamp}.wav"

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(recording)

    file_size = os.path.getsize(filename)

    print(f"📁 File {filename} has been saved with a size of {file_size} bytes.")

    return filename


def main():
    assistant = AssElevenPAF()
    assistant.setup()

    while True:
        try:
            input("🎧 Press Enter to start recording...")
            recording = record_audio(duration=duration, fs=fs, channels=channels)

            filename = create_audio_file(recording)

            transcription = assistant.transcribe(filename)
            print(f"📝 Your Input Transcription: '{transcription}'")

            response = assistant.think(transcription)
            print(f"🤖 Your Personal AI Assistant Response: '{response}'")

            assistant.speak(response)

            os.remove(filename)

            print("\nReady for next interaction. Press Ctrl+C to exit.")
        except KeyboardInterrupt:
            print("\nExiting the program.")
            break


if __name__ == "__main__":
    main()
