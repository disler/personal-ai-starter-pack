import abc
import time
import functools
import uuid
import requests
import sounddevice as sd
import wave
import os
import json
from datetime import datetime
import assemblyai as aai
from elevenlabs import play
from elevenlabs.client import ElevenLabs
from PIL import Image
import subprocess
from modules.constants import (
    OPENAI_IMG_AGENT_DIR,
    ELEVEN_LABS_CRINGE_VOICE,
    ELEVEN_LABS_PRIMARY_SOLID_VOICE,
)
from modules.simple_llm import build_mini_model, build_new_gpt4o, prompt
from dotenv import load_dotenv
import openai
from groq import Groq

from modules.typings import (
    ConvertImageParams,
    GenerateImageParams,
    ImageRatio,
    Style,
    ResizeImageParams,
    OpenImageDirParams,
)


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
            model="tts-1-hd", voice="shimmer", input=text, response_format="aac"
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
            voice=ELEVEN_LABS_CRINGE_VOICE,
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


class OpenAISuperPAF(OpenAIPAF):
    def setup(self):
        super().setup()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.weak_model = build_mini_model()
        self.download_directory = os.path.join(os.getcwd(), OPENAI_IMG_AGENT_DIR)
        if not os.path.exists(self.download_directory):
            os.makedirs(self.download_directory)

    def generate_image(self, generate_image_params: GenerateImageParams) -> bool:

        # handle defaults
        if generate_image_params.image_ratio is None:
            generate_image_params.image_ratio = ImageRatio.SQUARE
        if generate_image_params.quality is None:
            generate_image_params.quality = "hd"
        if generate_image_params.style is None:
            generate_image_params.style = Style.NATURAL

        client = openai.OpenAI()
        subdirectory = os.path.join(self.download_directory)
        if not os.path.exists(subdirectory):
            os.makedirs(subdirectory)

        for index, prompt in enumerate(generate_image_params.prompts):
            print(f"🖼️ Generating image {index + 1} with prompt: {prompt}")
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=generate_image_params.image_ratio.value,
                quality=generate_image_params.quality,
                n=1,
                style=generate_image_params.style.value,
            )
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            image_path = os.path.join(subdirectory, f"version_{index}.png")
            with open(image_path, "wb") as file:
                file.write(image_response.content)

        return True

    def convert_image(self, convert_image_params: ConvertImageParams) -> bool:
        subdirectory = os.path.join(self.download_directory)
        if not os.path.exists(subdirectory):
            os.makedirs(subdirectory)

        for index in convert_image_params.version_numbers:
            input_path = os.path.join(subdirectory, f"version_{index}.png")
            if not os.path.exists(input_path):
                print(f"🟡 Warning: File {input_path} does not exist. Skipping.")
                continue

            output_path = os.path.join(
                subdirectory, f"version_{index}.{convert_image_params.image_format}"
            )

            try:
                with Image.open(input_path) as img:
                    img.save(
                        output_path,
                        format=convert_image_params.image_format.value.upper(),
                    )
                print(f"🖼️ Converted {input_path} to {output_path}")
            except Exception as e:
                print(f"Error converting {input_path}: {str(e)}")
                return False

        return True

    def resize_image(self, resize_image_params: ResizeImageParams) -> bool:
        subdirectory = os.path.join(self.download_directory)
        if not os.path.exists(subdirectory):
            os.makedirs(subdirectory)

        for index in resize_image_params.version_numbers:
            input_path = os.path.join(subdirectory, f"version_{index}.png")
            if not os.path.exists(input_path):
                print(f"🟡 Warning: File {input_path} does not exist. Skipping.")
                continue

            output_path = os.path.join(
                subdirectory,
                f"version_{index}_resized_w{resize_image_params.width}_h{resize_image_params.height}.png",
            )

            try:
                with Image.open(input_path) as img:
                    resized_img = img.resize(
                        (resize_image_params.width, resize_image_params.height)
                    )
                    resized_img.save(output_path)
                print(f"🖼️ Resized {input_path} to {output_path}")
            except Exception as e:
                print(f"Error resizing {input_path}: {str(e)}")
                return False

        return True

    def open_image_directory(self, open_image_dir_params: OpenImageDirParams) -> bool:
        try:
            if os.name == 'nt':  # For Windows
                os.startfile(self.download_directory)
            elif os.name == 'posix':  # For macOS and Linux
                subprocess.call(['open', self.download_directory])
            print(f"📂 Opened image directory: {self.download_directory}")
            return True
        except Exception as e:
            print(f"Error opening image directory: {str(e)}")
            return False

    def think(self, thought: str) -> str:
        client = openai.OpenAI()
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": thought},
            ],
            tools=[
                openai.pydantic_function_tool(GenerateImageParams),
                openai.pydantic_function_tool(ConvertImageParams),
                openai.pydantic_function_tool(ResizeImageParams),
                openai.pydantic_function_tool(OpenImageDirParams),
            ],
        )

        message = completion.choices[0].message

        if message.tool_calls:

            tool_call = message.tool_calls[0]

            pretty_parsed_arguments = (
                tool_call.function.parsed_arguments.model_dump_json(indent=2)
            )

            print(
                f"""Tool call found: '{tool_call.function.name}(
{pretty_parsed_arguments}
)'. 
Calling..."""
            )

            success = False

            tool_call_success_prompt = f"Quickly let your human companion know that you've run the '{tool_call.function.name}' tool. Respond in a short, conversational manner, no fluff."

            tool_function_map = {
                "GenerateImageParams": self.generate_image,
                "ConvertImageParams": self.convert_image,
                "ResizeImageParams": self.resize_image,
                "OpenImageDirParams": self.open_image_directory,
            }

            if tool_call.function.name in tool_function_map:
                # 🚀 GUARANTEED OUTPUT STRUCTURE 🚀
                params = tool_call.function.parsed_arguments
                success = tool_function_map[tool_call.function.name](params)
                tool_call_success_prompt = f"Quickly let your human companion know that you've run the '{tool_call.function.name}' tool. Respond in a short, conversational manner, no fluff."
            else:
                success = False
                tool_call_success_prompt = (
                    "An unknown tool was called. Please try again."
                )

            if success:
                return prompt(self.weak_model, tool_call_success_prompt)

        else:
            # just a normal thought
            return prompt(self.weak_model, thought)
