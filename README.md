# YoungBot
An extensible Telegram bot implementation written in Python.


## Installation
First, clone the Github repository to your local filesystem:
```bash
git clone https://github.com/willemli/YoungBot.git
```

Second, install the pip requirements
```bash
pip3 install -r requirements.txt
```

Finally, you need to have a valid `settings.json` file.\
An example of this is listed below:
```json
{
    "token": "123456789:K49v2qnmMVtzNcCzOS-vv6iFofE7mk2F4G1",
    "user_id": 12345678,
    "storage_file": "storage.json",
    "failed_log": "failed.log",

    "extensions": {
        "shell": {
            "global_settings": ["user_id"]
        },
        "vote": {
            "disabled": true
        },
    }
}
```
(obviously replace `token` and `user_id` with your own values)


To start the bot, simply run this command:
```bash
python3 main.py
```


## Contributing
You are welcome to contribute your own extensions or bot core updates.

 
If you would like to see an example of a simple extension, take a look below:

```python
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
            'text': 'Hi' + str(self.storage.get('count'))
        })
```
More examples can be seen in the repository.
