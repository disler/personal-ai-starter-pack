import abc
import time
import functools
import sounddevice as sd
import wave
import os
import json
from datetime import datetime
import assemblyai as aai
from elevenlabs import play
from elevenlabs.client import ElevenLabs
from modules.constants import load_config
from modules.simple_llm import build_mini_model, prompt
import threading
from dotenv import load_dotenv
import openai
from groq import Groq

# Get the active configuration
config = load_config()

class PersonalAssistantFramework(abc.ABC):
    @staticmethod
    def timeit_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            print(
                f"⏰ {args[0].__class__.__name__} - {func.__name__}() took {duration:.2f} seconds"
            )

            json_file = f"{args[0].__class__.__name__}_time_table.json"

            # Read existing data or create an empty list
            if os.path.exists(json_file):
                with open(json_file, "r") as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = []
            else:
                data = []

            # Create new time record
            time_record = {
                "assistant": args[0].__class__.__name__,
                "function": func.__name__,
                "duration": f"{duration:.2f}",
                "position": 0,  # New entry always at the top
            }

            # Update positions of existing records
            for record in data:
                record["position"] += 1

            # Insert new record at the beginning
            data.insert(0, time_record)

            # Sort data by position
            data.sort(key=lambda x: x["position"])

            # Write updated data back to file
            with open(json_file, "w") as file:
                json.dump(data, file, indent=2)

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
            voice=config["ELEVEN_LABS_VOICE"],
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
        audio = self.generate_voice_audio(text)
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
                model="whisper-1",  # this points to whisper v2. See Docs (https://platform.openai.com/docs/api-reference/audio/createTranscription)
                file=audio_file,
            )
        return transcript.text

    @PersonalAssistantFramework.timeit_decorator
    def generate_voice_audio(self, text: str):
        response = openai.audio.speech.create(
            model="tts-1-hd", voice=config["OPENAI_VOICE"], input=text, response_format="aac"
        )
        audio_bytes = b"".join(list(response.iter_bytes()))
        return audio_bytes

    def speak(self, text: str):
        audio = self.generate_voice_audio(text)
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
            voice=config["ELEVEN_LABS_VOICE"],
            model="eleven_turbo_v2_5",
            stream=False,
        )
        audio_bytes = b"".join(list(audio_generator))
        return audio_bytes

    def speak(self, text: str):
        audio = self.generate_voice_audio(text)
        play(audio)

    @PersonalAssistantFramework.timeit_decorator
    def think(self, thought: str) -> str:
        return prompt(self.llm_model, thought)
