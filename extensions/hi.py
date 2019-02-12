import telepot

class Hi:

    def __init__(self, **kwargs):
        self.message_sender = kwargs.get('message_sender')
        self.settings = kwargs.get('settings')
        self.storage = kwargs.get('storage')

        if not self.storage.exists('count'):
            self.storage.put('count', 0)

    def get_commands(self):
        return [
            {'prefix': 'hi', 'description': 'Say hi!'},
        ]

    def get_tasks(self):
        return []

    def chat(self, message):
        content_type, chat_type, chat_id = telepot.glance(message)
        user_id = message['from']['id']

        self.storage.put('count', self.storage.get('count')+1)

        self.message_sender.enqueue({
            'chat_id': chat_id,
            'text': 'HUTS ' + str(self.storage.get('count'))
        })