import os
import google.cloud.texttospeech as tts
from dotenv import load_dotenv
import sounddevice as sd
import soundfile as sf

load_dotenv()

LANGUAGE_CODE = "en-US"
VOICE_NAME = "en-US-Neural2-F"


def say_sum_shit(text: str):
    text_input = tts.SynthesisInput(text=text)
    voice_params = tts.VoiceSelectionParams(
        language_code=LANGUAGE_CODE, name=VOICE_NAME
    )
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input, voice=voice_params, audio_config=audio_config
    )

    with open("audio.wav", "wb") as out:
        out.write(response.audio_content)

    data, fs = sf.read("audio.wav", dtype="float32")
    sd.play(data, fs)
    sd.wait()
    os.remove("audio.wav")
