import time
from typing import List
from modules.typings import Interaction
import sounddevice as sd
import wave
import os
from datetime import datetime
from assistants.assistants import AssElevenPAF, GroqElevenPAF, OpenAIPAF
import threading
from dotenv import load_dotenv
from modules.constants import (
    PERSONAL_AI_ASSISTANT_PROMPT_HEAD,
    FS,
    CHANNELS,
    DURATION,
    CONVO_TRAIL_CUTOFF,
    ASSISTANT_TYPE,
)

from modules.typings import Interaction

load_dotenv()


def record_audio(duration=DURATION, fs=FS, channels=CHANNELS):
    """
    Simple function to record audio from the microphone.
    Gives you DURATION seconds of audio to speak into the microphone.
    After DURATION seconds, the recording will stop.
    Hit enter to stop the recording at any time.
    """

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
    """
    Creates an audio file from the recording.
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"audio_{timestamp}.wav"

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(FS)
        wf.writeframes(recording)

    file_size = os.path.getsize(filename)

    print(f"📁 File {filename} has been saved with a size of {file_size} bytes.")

    return filename


def build_prompt(latest_input: str, previous_interactions: List[Interaction]) -> str:
    previous_interactions_str = "\n".join(
        [
            f"""<interaction>
    <role>{interaction.role}</role>
    <content>{interaction.content}</content>
</interaction>"""
            for interaction in previous_interactions
        ]
    )
    prepared_prompt = PERSONAL_AI_ASSISTANT_PROMPT_HEAD.replace(
        "[[previous_interactions]]", previous_interactions_str
    ).replace("[[latest_input]]", latest_input)

    return prepared_prompt


def main():
    """
    In a loop, we:
    1. Press enter to start recording
    2. Record audio from the microphone for N seconds
    3. When we press enter again, we create an audio file from the recording
    4. Transcribe the audio file
    5. Our AI assistant thinks (prompt) of a response to the transcription
    6. Our AI assistant speaks the response
    7. Delete the audio file
    8. Update previous interactions
    """

    previous_interactions: List[Interaction] = []

    if ASSISTANT_TYPE == "OpenAIPAF":

        assistant = OpenAIPAF()
        print("🚀 Initialized OpenAI Personal AI Assistant...")

    elif ASSISTANT_TYPE == "AssElevenPAF":

        assistant = AssElevenPAF()
        print("🚀 Initialized AssemblyAI-ElevenLabs Personal AI Assistant...")

    elif ASSISTANT_TYPE == "GroqElevenPAF":

        assistant = GroqElevenPAF()
        print("🚀 Initialized Groq-ElevenLabs Personal AI Assistant...")

    else:
        raise ValueError(f"Invalid assistant type: {ASSISTANT_TYPE}")

    assistant.setup()

    while True:
        try:
            input("🎧 Press Enter to start recording...")
            recording = record_audio(duration=DURATION, fs=FS, channels=CHANNELS)

            filename = create_audio_file(recording)
            transcription = assistant.transcribe(filename)

            print(f"📝 Your Input Transcription: '{transcription}'")

            prompt = build_prompt(transcription, previous_interactions)
            response = assistant.think(prompt)

            print(f"🤖 Your Personal AI Assistant Response: '{response}'")

            assistant.speak(response)

            os.remove(filename)

            # Update previous interactions
            previous_interactions.append(
                Interaction(role="human", content=transcription)
            )
            previous_interactions.append(
                Interaction(role="assistant", content=response)
            )

            # Keep only the last CONVO_TRAIL_CUTOFF interactions
            if len(previous_interactions) > CONVO_TRAIL_CUTOFF:
                previous_interactions = previous_interactions[-CONVO_TRAIL_CUTOFF:]

            print("\nReady for next interaction. Press Ctrl+C to exit.")
        except KeyboardInterrupt:
            print("\nExiting the program.")
            break


if __name__ == "__main__":
    main()
