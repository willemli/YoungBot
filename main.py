import subprocess
import threading
import sys

import telepot
from telepot.loop import MessageLoop

from core.settingsmanager import SettingsManager
from core.storagemanager import StorageManager
from core.commandmanager import CommandManager
from core.messagesender import MessageSender
from core.taskmanager import TaskManager
from core.extensionmanager import ExtensionManager
from core.workersmanager import WorkersManager
from core.messagereceiver import MessageReceiver


# Startup
print('\n=== Starting YoungBot ===')

# Read settings
settings_file = 'settings.json'

if len(sys.argv) > 1:
    settings_file = sys.argv[1]

settings_manager = SettingsManager(settings_file)

# Initialize telepot bot
bot = telepot.Bot(settings_manager.get('token'))

# Initialize storage manager
storage_manager = StorageManager(settings_manager.get('storage_file'))

# Initialize command manager
command_manager = CommandManager()

# Initialize message sender
message_sender = MessageSender(
    bot = bot,
    settings_manager = settings_manager
)

# Initialize task manager
task_manager = TaskManager()

# Initialize extension manager
extension_manager = ExtensionManager(
    command_manager = command_manager,
    task_manager = task_manager,
    message_sender = message_sender,
    settings_manager = settings_manager,
    storage_manager = storage_manager
)
extension_manager.load_all(settings_manager.get('extensions'))

# Start task manager
task_manager.set_extension_manager(extension_manager)
task_manager.start()

# Initialize workers manager
workers_manager = WorkersManager(extension_manager)

# Message receiver
message_receiver = MessageReceiver(
    bot = bot,
    command_manager = command_manager,
    message_sender = message_sender,
    workers_manager = workers_manager,
    extension_manager = extension_manager,
    settings_manager = settings_manager,
    storage_manager = storage_manager
)

# Start bot
message_sender.send({
    'chat_id': settings_manager.get('user_id'),
    'text': '<b>=== YoungBot has been started ===</b>'
})
print('=== YoungBot has been started ===\n')
MessageLoop(bot, {
    'chat': message_receiver.handle_chat, 
    'callback_query': message_receiver.handle_callback
}).run_forever()
