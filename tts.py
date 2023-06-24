import dataclasses
import os
import pyttsx3


@dataclasses.dataclass
class Voice():
    id: str
    name: str


class TTS():
    voices: list[Voice]

    def __init__(self):
        self.engine = pyttsx3.init()
        self.init_voices()

    def init_voices(self):
        self.voices = []
        for voice in self.engine.getProperty('voices'):
            self.voices.append(Voice(voice.id, voice.name))

    def get_voice_id_from_name(self, name):
        for voice in self.voices:
            if name in voice.name:
                return voice.id
        return None

    def set_voices(self, name):
        id = self.get_voice_id_from_name(name)
        if id:
            self.engine.setProperty('voice', id)
        else:
            print(f"No voice found for language '{id}'")

    def save_to_file(self, text: str, output: str):
        if os.path.exists(output):
            os.remove(output)
        self.engine.save_to_file(text, output)
        self.engine.runAndWait()
