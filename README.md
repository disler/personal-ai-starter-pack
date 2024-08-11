# Fast Personal AI Assistant & Structured Output
>
> A quick start personal AI assistant framework using OpenAI, Groq, AssemblyAI and ElevenLabs.
>
> And a breakdown of the reliability of AI agents with the new structured output.

![reliable-ai-agents.png](./img/reliable-ai-agents.png)
![own-your-ai](./img/own-your-ai.png)


## Setup

- Create and activate virtual environment:
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
  ```

- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

- Set up environment variables:
  ```bash
  cp .env.sample .env
  # Edit .env file and add your API keys
  ```
  `I recommend starting with the OpenAI assistant since you only need to set up the OpenAI API key.`.

- Run the main script:
  ```bash
  python main.py
  ```

- Run the structured output script:
  ```bash
  python structured_outputs_example.py
  ```

- Press `Enter` to start recording, and `Enter` again to stop recording.

- Adjust the maximum duration of the recording in `constants.py: DURATION`

- Update configuration variables in `constants.py`
  - Tweak naming.
  - Update the prompt to your liking.
  - Update the assistant type to the one you want to use.

## Watch the walk through video
- [Coding RELIABLE AI Agents: Legit Structured Outputs Use Cases (Strawberry Agent?)](https://youtu.be/PoO7Zjsvx0k)
- [CONTROL your Personal AI Assistant with GPT-4o mini & ElevenLabs](https://youtu.be/ikaKpfUOb0U)

## Resources
- https://openai.com/index/introducing-structured-outputs-in-the-api/
- https://www.assemblyai.com/ 
- https://console.groq.com/docs/speech-text
- https://console.groq.com/docs/libraries
- https://platform.openai.com/docs/guides/speech-to-text
- https://platform.openai.com/docs/guides/text-to-speech
- https://platform.openai.com/docs/api-reference/audio#audio/createTranscription-prompt
- https://openai.com/api/pricing/
