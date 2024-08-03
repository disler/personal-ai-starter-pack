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
from modules.constants import ELEVEN_LABS_CRINGE_VOICE, ELEVEN_LABS_PRIMARY_SOLID_VOICE
from modules.simple_llm import build_mini_model, prompt
import threading
from dotenv import load_dotenv
import openai
import openai
from groq import Groq


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
        audio_generator = self.elevenlabs_client.generate(
            text=text,
            voice=ELEVEN_LABS_PRIMARY_SOLID_VOICE,
            model="eleven_turbo_v2",
            stream=False,
        )
        audio_bytes = b"".join(list(audio_generator))
        return audio_bytes

    @PersonalAssistantFramework.timeit_decorator
    def transcribe(self, file_path):
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(file_path)
        return transcript.text

    def speak(self, text: str):
        print(f"Start generating voice audio for {text}")
        audio = self.generate_voice_audio(text)
        print(f"End generating voice audio for {text}")
        play(audio)

    @PersonalAssistantFramework.timeit_decorator
    def think(self, thought: str) -> str:
        return prompt(self.llm_model, thought)


class OpenAIPAF(PersonalAssistantFramework):
    def setup(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.llm_model = build_mini_model()

    @PersonalAssistantFramework.timeit_decorator
    def transcribe(self, file_path):
        with open(file_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1", file=audio_file
            )
        return transcript.text

    @PersonalAssistantFramework.timeit_decorator
    def generate_voice_audio(self, text: str):
        response = openai.audio.speech.create(
            model="tts-1-hd", voice="shimmer", input=text, response_format="aac"
        )
        audio_bytes = b"".join(list(response.iter_bytes()))
        return audio_bytes

    def speak(self, text: str):
        print(f"Start generating voice audio for {text}")
        audio = self.generate_voice_audio(text)
        print(f"End generating voice audio for {text}, len: {len(audio)}")
        play(audio)

    @PersonalAssistantFramework.timeit_decorator
    def think(self, thought: str) -> str:
        return prompt(self.llm_model, thought)


class GroqElevenPAF(PersonalAssistantFramework):
    def setup(self):
        self.groq_client = Groq()
        self.elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVEN_API_KEY"))
        self.llm_model = build_mini_model()

    @PersonalAssistantFramework.timeit_decorator
    def transcribe(self, file_path):
        with open(file_path, "rb") as file:
            transcription = self.groq_client.audio.transcriptions.create(
                file=(file_path, file.read()),
                model="whisper-large-v3",
                response_format="text",
            )
        return str(transcription)

    @PersonalAssistantFramework.timeit_decorator
    def generate_voice_audio(self, text: str):
        audio_generator = self.elevenlabs_client.generate(
            text=text,
            voice=ELEVEN_LABS_CRINGE_VOICE,
            model="eleven_turbo_v2_5",
            stream=False,
        )
        audio_bytes = b"".join(list(audio_generator))
        return audio_bytes

    def speak(self, text: str):
        print(f"Start generating voice audio for {text}")
        audio = self.generate_voice_audio(text)
        print(f"End generating voice audio for {text}, len: {len(audio)}")
        play(audio)

    @PersonalAssistantFramework.timeit_decorator
    def think(self, thought: str) -> str:
        return prompt(self.llm_model, thought)
