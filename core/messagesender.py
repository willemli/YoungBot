import telepot
import threading
import time
import copy

import json

class MessageSender:

    # List of all messages to send
    _queue = []

    # History of all messages sent
    # Not used yet
    _sent = []

    # Message types that are files
    messageTypeFiles = ['document', 'audio', 'photo', 'video']

    def __init__(self, **kwargs):
        print('[MessageSender] Created')

        self.bot = kwargs.get('bot')
        self.settings_manager = kwargs.get('settings_manager')
        queue_handler_thread = threading.Thread(target=self.queue_handler)
        queue_handler_thread.start()

    
    # Add item to queue
    def enqueue(self, message):
        self._queue.append(message)
    

    '''
    Sends a message immediately
    and returns the sent message

    (wait to send message if too many?)
    '''
    def send(self, message):
        self._sent.append({'chat_id': message.get('chat_id'), 'at': time.time()})

        message_type = message.pop('type', 'text')

        if not 'parse_mode' in message:
            message.update({'parse_mode': 'HTML'})

        # Text messages
        if message_type == 'text':
            return self.bot.sendMessage( **message)

        # Text edits
        elif message_type == 'edit':
            msg_identifier = message['msg_identifier']
            message = self.getNewestEdit(msg_identifier, message)
            if 'type' in message:
                message.pop('type')
            message['parse_mode'] = 'HTML'
            self.deleteOldEdits(msg_identifier)
            return self.bot.editMessageText(**message)

        # Send file
        elif message_type in self.messageTypeFiles:
            chat_id = message.pop('chat_id')
            self.bot.sendChatAction(chat_id, 'upload_' + message_type)

            file_name = message.pop('file_name')
            if not file_name.startswith('http'):
                file_name = open(file_name, 'rb')

            if message_type == 'document':
                return self.bot.sendDocument(chat_id, file_name, **message)
            elif message_type == 'audio':
                return self.bot.sendAudio(chat_id, file_name, **message)
            elif message_type == 'photo':
                return self.bot.sendPhoto(chat_id, file_name, **message)
            elif message_type == 'video':
                return self.bot.sendVideo(chat_id, file_name, **message)

        # Media group
        elif message_type == 'media_group':
            message.pop('parse_mode')
            chat_id = message.pop('chat_id')
            self.bot.sendChatAction(chat_id, 'upload_photo')
            self.bot.sendMediaGroup(chat_id, **message)

        # Forwards
        elif message_type == 'forward':
            self.bot.forwardMessage(**message)

        #print(self._sent)

    '''
    https://core.telegram.org/bots/api#answercallbackquery
    '''
    def answerCallbackQuery(self, callback_query_id, text):
        self.bot.answerCallbackQuery(callback_query_id, text)

    
    '''
    Handles messages in the queue
    '''
    def queue_handler(self):
        print('[MessageSender-QueueHandler] Started')

        while True:
            if self._queue:
                message = self._queue.pop(0)
                tries = message.pop('_tries', 0)
                
                if tries < 3:
                    message_copy = copy.deepcopy(message)
                    try:
                        self.send(message)
                        time.sleep(0.75)
                    except Exception as e:
                        tries += 1
                        print('[MessageSender-QueueHandler] Attempt ' + str(tries) + ': ' + str(e))
                        message_copy['_tries'] = tries
                        self._queue.append(message_copy)
                        time.sleep(1)
                else:
                    try:
                        log_file = self.settings_manager.get('failed_log')
                        print('[MessageSender-QueueHandler] Could not send message, appending to ' + log_file)
                        with open(log_file, 'a') as f:
                            f.write(json.dumps(message))
                            f.write('\n')
                    except Exception as e:
                        print('[MessageSender-QueueHandler] Could append failed message to failed log!')

            time.sleep(0.01)

    
    '''
    Deletes older edits that contain the identifier
    '''
    def deleteOldEdits(self, msg_identifier):
        for item in list(self._queue):
            if 'msg_identifier' in item and item['msg_identifier'] == msg_identifier:
                self._queue.remove(item)

    '''
    Returns the newest message that contains the identifier
    If no newer message is present, return the original message
    '''
    def getNewestEdit(self, msg_identifier, originalMessage):
        for item in reversed(self._queue):
            if 'msg_identifier' in item and item['msg_identifier'] == msg_identifier:
                return item
        return originalMessage
