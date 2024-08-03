# Fast Personal AI Assistant
> Fast TTS & STT

## Resources
https://console.groq.com/docs/speech-text
https://console.groq.com/docs/libraries
https://platform.openai.com/docs/guides/speech-to-text
https://platform.openai.com/docs/guides/text-to-speech
https://platform.openai.com/docs/api-reference/audio#audio/createTranscription-prompt
https://openai.com/api/pricing/

## OpenAI STT Docs

```
Speech to text
Learn how to turn audio into text

Introduction
The Audio API provides two speech to text endpoints, transcriptions and translations, based on our state-of-the-art open source large-v2 Whisper model. They can be used to:

Transcribe audio into whatever language the audio is in.
Translate and transcribe the audio into english.
File uploads are currently limited to 25 MB and the following input file types are supported: mp3, mp4, mpeg, mpga, m4a, wav, and webm.

Quickstart
Transcriptions
The transcriptions API takes as input the audio file you want to transcribe and the desired output file format for the transcription of the audio. We currently support multiple input and output file formats.

Transcribe audio
python

python
from openai import OpenAI
client = OpenAI()

audio_file= open("/path/to/file/audio.mp3", "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file
)
print(transcription.text)
By default, the response type will be json with the raw text included.

{
  "text": "Imagine the wildest idea that you've ever had, and you're curious about how it might scale to something that's a 100, a 1,000 times bigger.
....
}
The Audio API also allows you to set additional parameters in a request. For example, if you want to set the response_format as text, your request would look like the following:

Additional options
python

python
from openai import OpenAI
client = OpenAI()

audio_file = open("/path/to/file/speech.mp3", "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file, 
  response_format="text"
)
print(transcription.text)
The API Reference includes the full list of available parameters.

Translations
The translations API takes as input the audio file in any of the supported languages and transcribes, if necessary, the audio into English. This differs from our /Transcriptions endpoint since the output is not in the original input language and is instead translated to English text.

Translate audio
python

python
from openai import OpenAI
client = OpenAI()

audio_file= open("/path/to/file/german.mp3", "rb")
translation = client.audio.translations.create(
  model="whisper-1", 
  file=audio_file
)
print(translation.text)
In this case, the inputted audio was german and the outputted text looks like:

Hello, my name is Wolfgang and I come from Germany. Where are you heading today?
We only support translation into English at this time.

Supported languages
We currently support the following languages through both the transcriptions and translations endpoint:

Afrikaans, Arabic, Armenian, Azerbaijani, Belarusian, Bosnian, Bulgarian, Catalan, Chinese, Croatian, Czech, Danish, Dutch, English, Estonian, Finnish, French, Galician, German, Greek, Hebrew, Hindi, Hungarian, Icelandic, Indonesian, Italian, Japanese, Kannada, Kazakh, Korean, Latvian, Lithuanian, Macedonian, Malay, Marathi, Maori, Nepali, Norwegian, Persian, Polish, Portuguese, Romanian, Russian, Serbian, Slovak, Slovenian, Spanish, Swahili, Swedish, Tagalog, Tamil, Thai, Turkish, Ukrainian, Urdu, Vietnamese, and Welsh.

While the underlying model was trained on 98 languages, we only list the languages that exceeded <50% word error rate (WER) which is an industry standard benchmark for speech to text model accuracy. The model will return results for languages not listed above but the quality will be low.

Timestamps
By default, the Whisper API will output a transcript of the provided audio in text. The timestamp_granularities[] parameter enables a more structured and timestamped json output format, with timestamps at the segment, word level, or both. This enables word-level precision for transcripts and video edits, which allows for the removal of specific frames tied to individual words.

Timestamp options
python

python
from openai import OpenAI
client = OpenAI()

audio_file = open("speech.mp3", "rb")
transcript = client.audio.transcriptions.create(
  file=audio_file,
  model="whisper-1",
  response_format="verbose_json",
  timestamp_granularities=["word"]
)

print(transcript.words)
Longer inputs
By default, the Whisper API only supports files that are less than 25 MB. If you have an audio file that is longer than that, you will need to break it up into chunks of 25 MB's or less or used a compressed audio format. To get the best performance, we suggest that you avoid breaking the audio up mid-sentence as this may cause some context to be lost.

One way to handle this is to use the PyDub open source Python package to split the audio:

from pydub import AudioSegment

song = AudioSegment.from_mp3("good_morning.mp3")

# PyDub handles time in milliseconds
ten_minutes = 10 * 60 * 1000

first_10_minutes = song[:ten_minutes]

first_10_minutes.export("good_morning_10.mp3", format="mp3")
OpenAI makes no guarantees about the usability or security of 3rd party software like PyDub.

Prompting
You can use a prompt to improve the quality of the transcripts generated by the Whisper API. The model will try to match the style of the prompt, so it will be more likely to use capitalization and punctuation if the prompt does too. However, the current prompting system is much more limited than our other language models and only provides limited control over the generated audio. Here are some examples of how prompting can help in different scenarios:

Prompts can be very helpful for correcting specific words or acronyms that the model may misrecognize in the audio. For example, the following prompt improves the transcription of the words DALL·E and GPT-3, which were previously written as "GDP 3" and "DALI": "The transcript is about OpenAI which makes technology like DALL·E, GPT-3, and ChatGPT with the hope of one day building an AGI system that benefits all of humanity"
To preserve the context of a file that was split into segments, you can prompt the model with the transcript of the preceding segment. This will make the transcript more accurate, as the model will use the relevant information from the previous audio. The model will only consider the final 224 tokens of the prompt and ignore anything earlier. For multilingual inputs, Whisper uses a custom tokenizer. For English only inputs, it uses the standard GPT-2 tokenizer which are both accessible through the open source Whisper Python package.
Sometimes the model might skip punctuation in the transcript. You can avoid this by using a simple prompt that includes punctuation: "Hello, welcome to my lecture."
The model may also leave out common filler words in the audio. If you want to keep the filler words in your transcript, you can use a prompt that contains them: "Umm, let me think like, hmm... Okay, here's what I'm, like, thinking."
Some languages can be written in different ways, such as simplified or traditional Chinese. The model might not always use the writing style that you want for your transcript by default. You can improve this by using a prompt in your preferred writing style.
Improving reliability
As we explored in the prompting section, one of the most common challenges faced when using Whisper is the model often does not recognize uncommon words or acronyms. To address this, we have highlighted different techniques which improve the reliability of Whisper in these cases:
```

# OpenAI TTS Docs

```
Text to speech
Learn how to turn text into lifelike spoken audio

Overview
The Audio API provides a speech endpoint based on our TTS (text-to-speech) model. It comes with 6 built-in voices and can be used to:

Narrate a written blog post
Produce spoken audio in multiple languages
Give real time audio output using streaming
Here is an example of the alloy voice:

Please note that our usage policies require you to provide a clear disclosure to end users that the TTS voice they are hearing is AI-generated and not a human voice.

Quickstart
The speech endpoint takes in three key inputs: the model, the text that should be turned into audio, and the voice to be used for the audio generation. A simple request would look like the following:

Generate spoken audio from input text
python

python
from pathlib import Path
from openai import OpenAI
client = OpenAI()

speech_file_path = Path(__file__).parent / "speech.mp3"
response = client.audio.speech.create(
  model="tts-1",
  voice="alloy",
  input="Today is a wonderful day to build something people love!"
)

response.stream_to_file(speech_file_path)
By default, the endpoint will output a MP3 file of the spoken audio but it can also be configured to output any of our supported formats.

Audio quality
For real-time applications, the standard tts-1 model provides the lowest latency but at a lower quality than the tts-1-hd model. Due to the way the audio is generated, tts-1 is likely to generate content that has more static in certain situations than tts-1-hd. In some cases, the audio may not have noticeable differences depending on your listening device and the individual person.

Voice options
Experiment with different voices (alloy, echo, fable, onyx, nova, and shimmer) to find one that matches your desired tone and audience. The current voices are optimized for English.

Alloy
Echo
Fable
Onyx
Nova
Shimmer
Streaming real time audio
The Speech API provides support for real time audio streaming using chunk transfer encoding. This means that the audio is able to be played before the full file has been generated and made accessible.

from openai import OpenAI

client = OpenAI()

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello world! This is a streaming test.",
)

response.stream_to_file("output.mp3")
Supported output formats
The default response format is "mp3", but other formats like "opus", "aac", "flac", and "pcm" are available.

Opus: For internet streaming and communication, low latency.
AAC: For digital audio compression, preferred by YouTube, Android, iOS.
FLAC: For lossless audio compression, favored by audio enthusiasts for archiving.
WAV: Uncompressed WAV audio, suitable for low-latency applications to avoid decoding overhead.
PCM: Similar to WAV but containing the raw samples in 24kHz (16-bit signed, low-endian), without the header.
Supported languages
The TTS model generally follows the Whisper model in terms of language support. Whisper supports the following languages and performs well despite the current voices being optimized for English:

Afrikaans, Arabic, Armenian, Azerbaijani, Belarusian, Bosnian, Bulgarian, Catalan, Chinese, Croatian, Czech, Danish, Dutch, English, Estonian, Finnish, French, Galician, German, Greek, Hebrew, Hindi, Hungarian, Icelandic, Indonesian, Italian, Japanese, Kannada, Kazakh, Korean, Latvian, Lithuanian, Macedonian, Malay, Marathi, Maori, Nepali, Norwegian, Persian, Polish, Portuguese, Romanian, Russian, Serbian, Slovak, Slovenian, Spanish, Swahili, Swedish, Tagalog, Tamil, Thai, Turkish, Ukrainian, Urdu, Vietnamese, and Welsh.

You can generate spoken audio in these languages by providing the input text in the language of your choice.

FAQ
How can I control the emotional range of the generated audio?
There is no direct mechanism to control the emotional output of the audio generated. Certain factors may influence the output audio like capitalization or grammar but our internal tests with these have yielded mixed results.

Can I create a custom copy of my own voice?
No, this is not something we support.

Do I own the outputted audio files?
Yes, like with all outputs from our API, the person who created them owns the output. You are still required to inform end users that they are hearing audio generated by AI and not a real person talking to them.
```

## Groq TTS Docs

```
Speech to Text
Groq's Whisper API is capable of transcription and translation. Utilize our OpenAI-compatible endpoints to integrate high-quality audio processing directly into your applications.

API Endpoints
Transcriptions: Convert audio to text. https://api.groq.com/openai/v1/audio/transcriptions
Translations: Translate audio to English text. https://api.groq.com/openai/v1/audio/translations
Supported Models
Model ID: whisper-large-v3 This model provides state-of-the-art performance for both transcription and translation tasks.
Audio file limitations
File uploads are limited to 25 MB
The following input file types are supported: mp3, mp4, mpeg, mpga, m4a, wav, and webm
If a file contains multiple audio tracks, for example a video with dubs, only the first track will be transcribed

Whisper will downsample audio to 16,000 Hz mono before transcribing. This preprocessing can be performed client-side to reduce file size and allow longer files to be uploaded to groq. The following ffmpeg command can be used to reduce file size:


CopyCopy code
ffmpeg \
  -i <your file> \
  -ar 16000 \
  -ac 1 \
  -map 0:a: \
  <output file name>
Transcription Usage
Transcribe spoken words in audio or video files.


Optional Parameters:

prompt: Provide context or specify how to spell unfamiliar words
response_format: Define the output response format.
Default is "json"
Set to "verbose_json" to receive timestamps for audio segments
Set to "text" to return a text response
formats vtt and srt are not supported
temperature: Specify a value between 0 and 1 to control the translation output.
language: Specify the language for transcription (optional; Whisper will auto-detect if not specified)
Use ISO 639-1 language codes (e.g., "en" for English, "fr" for French, etc.).
Specifying a language may improve transcription accuracy and speed
timestamp_granularities[] is not supported
Code Overview
Python
JavaScript
curl
Copy
pip install groq

Copy
import os
from groq import Groq

client = Groq()
filename = os.path.dirname(__file__) + "/sample_audio.m4a"

with open(filename, "rb") as file:
    transcription = client.audio.transcriptions.create(
      file=(filename, file.read()),
      model="whisper-large-v3",
      prompt="Specify context or spelling",  # Optional
      response_format="json",  # Optional
      language="en",  # Optional
      temperature=0.0  # Optional
    )
    print(transcription.text)
Translation Usage
Translate spoken words in audio or video files to English.


Optional Parameters:

prompt: Provide context or specify how to spell unfamiliar words
response_format: Define the output response format
Default is "json"
Set to "verbose_json" to receive timestamps for audio segments
Set to "text" to return a text response
formats vtt and srt are not supported
temperature: Specify a value between 0 and 1 to control the translation output
Code Overview
Python
JavaScript
curl
Copy
pip install groq

Copy
import os
from groq import Groq

client = Groq()
filename = os.path.dirname(__file__) + "/sample_audio.m4a"

with open(filename, "rb") as file:
    translation = client.audio.translations.create(
      file=(filename, file.read()),
      model="whisper-large-v3",
      prompt="Specify context or spelling",  # Optional
      response_format="json",  # Optional
      temperature=0.0  # Optional
    )
    print(translation.text)
Prompting Guidelines
The prompt parameter is an optional input that helps the Whisper model to better understand the context of the audio segments and maintain a consistent writing style. When you provide a prompt parameter, Whisper treats it as a prior transcript from the same audio file, following the style of the prompt rather than the actual content. This means that the model will not follow instructions or attempt to execute commands contained within the prompt, unlike a chat completion prompt.


Tips for Using the prompt Parameter:

The prompt parameter should be in the same language as the audio file.
The prompt parameter is limited to 224 tokens.
The prompt parameter can be used to steer the model's output by denoting proper spellings or emulate a specific writing style or tone.
```