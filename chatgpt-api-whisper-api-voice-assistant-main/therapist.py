import gradio as gr
import openai, config, requests
import subprocess
openai.api_key = config.OPENAI_API_KEY

ELEVENLABS_API_ENDPOINT = 'https://api.elevenlabs.io/v1/text-to-speech/Aa0iTPUqaEt3cOOUKlrh'
ELEVENLABS_API_HEADERS = {
    'accept': 'audio/mpeg',
    'xi-api-key': '4d269bb08f203275502adc305a59789b',
    'Content-Type': 'application/json'
}

messages = [{"role": "system", "content": 'Pretend you are an Assistent. Your answers are mean and sassy'}]

def transcribe(audio):
    global messages

    audio_file = open(audio, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    print(transcript)

    messages.append({"role": "user", "content": transcript["text"]})

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    system_message = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": system_message})

    response_audio = requests.post(
    ELEVENLABS_API_ENDPOINT,
    headers=ELEVENLABS_API_HEADERS,
    json={
        "text": system_message,
        "voice_settings": {
            "stability": 0.8,
            "similarity_boost": 0.2
            }
        }
    )

    if response_audio.status_code == 200:
        with open("response.mp3", "wb") as f:
            f.write(response_audio.content)
        subprocess.call(["afplay", "response.mp3"])
    else:
        print("Error generating audio file")

    chat_transcript = ""
    for message in messages:
        if message['role'] != 'system':
            chat_transcript += message['role'] + ": " + message['content'] + "\n\n"

    return chat_transcript

ui = gr.Interface(fn=transcribe, inputs=gr.Audio(source="microphone", type="filepath"), outputs="text")
ui.launch()