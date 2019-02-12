import telepot
import subprocess
import io
import time
import cgi


'''
!!! WARNING !!!

THIS EXTENSION SHOULD ONLY BE USED FOR DEMONSTRATION PURPOSES.
NEVER RUN THIS ON A LIVE SERVER!!
'''


'''
Function to run command, returns output line per line
'''
def run(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    
    for lineOut in io.TextIOWrapper(process.stdout, encoding='utf-8'):
        if lineOut:
            yield lineOut.rstrip()

    for lineErr in io.TextIOWrapper(process.stderr, encoding='utf-8'):
        if lineErr:
            yield lineErr.rstrip()


class Shell:
    def __init__(self, **kwargs):
        self.message_sender = kwargs.get('message_sender')

    def get_commands(self):
        return [
            {'prefix': '>', 'description': 'Execute a shell command and get live feed output'},
        ]

    def get_tasks(self):
        return []

    def chat(self, message):
        content_type, chat_type, chat_id = telepot.glance(message)

        command = message['text'][1:]
        text = '<b>' + command + '</b>' + '\n\n'

        output_message = self.message_sender.send({
            'chat_id': chat_id,
            'text': text
        })
        msg_identifier = telepot.message_identifier(output_message)

        start = time.time()

        try:
            for line in run(command):
                oldText = text
                text += '<code>' + cgi.escape(line) + '\n</code>'
                if oldText != text and line.strip() != '':
                    self.message_sender.enqueue({'type': 'edit', 'msg_identifier': msg_identifier, 'text': text})
        except Exception as e:
            print('[ERROR] ' + str(e))
            self.message_sender.enqueue({'type': 'edit', 'msg_identifier': msg_identifier, 'text': text + str(e)})
            return
        
        end = time.time()
        text += '\n<i>Finished in ' + str(end-start) + ' seconds</i>'
        self.message_sender.enqueue({'type': 'edit', 'msg_identifier': msg_identifier, 'text': text})