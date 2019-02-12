import json
import telepot
import threading
import subprocess
import time
from datetime import timedelta

'''
Handles all incoming messages and creates workers
'''
class MessageReceiver:

    # Stats
    stats_timestamp_created = 0                   # Used for uptime
    stats_messages_received = 0
    stats_messages_handled = 0

    # _queue (list) containing all the messages to be processed
    _queue = []

    def __init__(self, **kwargs):
        print('[MessageReceiver] Created')

        self.bot = kwargs.get('bot')
        self.command_manager = kwargs.get('command_manager')
        self.message_sender = kwargs.get('message_sender')
        self.workers_manager = kwargs.get('workers_manager')
        self.settings_manager = kwargs.get('settings_manager')
        self.storage_manager = kwargs.get('storage_manager')
        self.extension_manager = kwargs.get('extension_manager')

        self.stats_timestamp_created = round(time.time())

        _queue_handler_thread = threading.Thread(target=self.queue_handler)
        _queue_handler_thread.start()


    '''
    Direct message handler, decides what to do with the message
    Messages with priority get handled here
    '''
    def handle_chat(self, message):
        content_type, chat_type, chat_id = telepot.glance(message)

        # Channels are not supported yet
        if message['chat']['type'] == 'channel':
            return

        if content_type == 'text':
            text = message['text']
            print('[MessageReceiver] ' + message['from']['first_name'] + ': ' + text)

            # Admin only commands
            if message['from']['id'] == self.settings_manager.get('user_id'):
                # Reload settings
                if text.startswith('!reloadsettings'):
                    self.settings_manager.load()
                elif text.startswith('!savestorage'):
                    self.storage_manager.save()
                elif text.startswith('!reloadstorage'):
                    self.storage_manager.load()
                # Load extension
                elif text.startswith('!load '):
                    extension_to_load = text.split('!load ')[1]

                    # Check if extension is loaded already
                    # If so, unload it first
                    if self.extension_manager.is_loaded(extension_to_load):
                        unloaded = self.extension_manager.unload(extension_to_load)
                        if not unloaded:
                            self.message_sender.send({
                                'chat_id': chat_id,
                                'text': 'Load ' + ('OK' if success else 'FAILED')
                            })
                            return

                    # Load the extension
                    success = self.extension_manager.load(extension_to_load)
                    self.message_sender.send({
                        'chat_id': chat_id,
                        'text': 'Load ' + ('OK' if success else 'FAILED')
                    })
                        
                # Unload extension
                elif text.startswith('!unload '):
                    extension_to_unload = text.split('!unload ')[1]
                    success = self.extension_manager.unload(extension_to_unload)
                    self.message_sender.send({
                        'chat_id': chat_id,
                        'text': 'Unload ' + ('OK' if success else 'FAILED')
                    })

                # View logs
                elif text.startswith('!logs'):
                    logs = subprocess.run(['tail', '-20', 'nohup.out'], stdout=subprocess.PIPE).stdout.decode('utf-8')
                    self.message_sender.send({
                        'chat_id': chat_id,
                        'text': '<code>' + logs + '</code>'
                    })

            # Show commands
            if text.startswith('/commands'):
                reply = '<b>=== Commands for YoungBot ===</b>\n\n'
                for command in self.command_manager.get_all_commands():
                    reply += '<b>'+command['prefix']+'</b> | <i>' + command['description'] + '</i>\n\n'
                self.message_sender.send({
                    'chat_id': chat_id,
                    'text': reply
                })
                return
            # View stats
            elif text.startswith('!stats'):
                reply = '<b>Stats for YoungBot</b>\n\n'
                reply += 'Uptime: ' + str(timedelta(seconds=round(time.time())-self.stats_timestamp_created)) + '\n'
                reply += 'Messages received: ' + str(self.stats_messages_received) + '\n'
                reply += 'Messages handled: ' + str(self.stats_messages_handled) + '\n'
                self.message_sender.send({
                    'chat_id': chat_id,
                    'text': reply
                })
                return

            # Check if message is a command before adding to _queue
            extension = self.command_manager.get_extension(message['text'])
            if extension:
                message['_type'] = 'chat'
                message['_extension'] = extension
                self._queue.append(message)
                self.stats_messages_handled += 1
            
        self.stats_messages_received += 1


    '''
    Direct callback handler, decides what to do with the callback
    '''
    def handle_callback(self, message):
        message['_type'] = 'callback'
        message['_extension'] = json.loads(message['data'])['_']
        self._queue.append(message)


    '''
    Handles messages in the _queue
    '''
    def queue_handler(self):
        print('[MessageReceiver-QueueHandler] Started')

        while True:
            try:

                # No items in _queue
                if self._queue:

                    # Take the first item in _queue
                    message = self._queue[0]

                    user_id = message['from']['id']
                    message_type = message.get('_type')
                    extension = message.get('_extension')

                    # Worker is alive
                    if self.workers_manager.worker_is_available(user_id):
                        # Pop the message
                        message = self._queue.pop(0)

                        # Start a new worker
                        self.workers_manager.create_worker(user_id, message_type, extension, message)

            except Exception as e:
                print('[MessageReceiver-QueueHandler] Error: '+str(e))

            time.sleep(0.01)
