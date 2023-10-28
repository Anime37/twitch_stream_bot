import requests

from fs import FS


class TelegramBot():
    def __init__(self):
        self.fs = FS()
        TOKEN_PATH = f'{FS.USER_DATA_PATH}telegram_bot_token'
        self.TOKEN = self.fs.read(TOKEN_PATH)
        self._get_chat_id()

    def _get_chat_id(self):
        if not self.TOKEN:
            return
        CHAT_ID_PATH = f'{FS.USER_DATA_PATH}telegram_bot_chat_id'
        self.CHAT_ID = self.fs.readint(CHAT_ID_PATH)
        if self.CHAT_ID:
            return
        url = f'https://api.telegram.org/bot{self.TOKEN}/getUpdates'
        r = requests.get(url)
        if r.status_code == 200:
            self.CHAT_ID = r.json()['result'][0]['message']['chat']['id']
            self.fs.write(CHAT_ID_PATH, str(self.CHAT_ID))

    def send_message(self, message: str):
        if not self.TOKEN:
            return
        url = f'https://api.telegram.org/bot{self.TOKEN}/sendMessage'
        data = {
            'chat_id': self.CHAT_ID,
            'text': message
        }
        response = requests.post(url, data=data)
        print(response)
