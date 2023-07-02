import dataclasses
import os
import random
import pyttsx3


@dataclasses.dataclass
class Voice():
    id: str
    name: str


class TTS():
    voices: list[Voice]

    def __init__(self):
        self.engine = pyttsx3.init()
        self._init_voices()

    def _init_voices(self):
        self.voices = []
        for voice in self.engine.getProperty('voices'):
            self.voices.append(Voice(voice.id, voice.name))

    def _set_voice_ids_from_name(self, name):
        self.voice_ids = []
        for voice in self.voices:
            if name in voice.name:
                self.voice_ids.append(voice.id)

    def set_voices(self, name):
        self._set_voice_ids_from_name(name)
        if not self.voice_ids:
            print(f"No voice found for language '{id}'")

    def _set_rand_voice(self):
        self.engine.setProperty('voice', random.choice(self.voice_ids))
        self.engine.setProperty('rate', random.randint(150, 250))

    def say(self, text):
        self._set_rand_voice()
        self.engine.say(text)
        self.engine.runAndWait()

    def save_to_file(self, text: str, output: str):
        if os.path.exists(output):
            os.remove(output)
        self._set_rand_voice()
        self.engine.save_to_file(text, output)
        self.engine.runAndWait()
