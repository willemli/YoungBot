import sys
import importlib
import traceback

from core.storagemanager import Storage


class ExtensionManager:
    
    extensions = []

    def __init__(self, **kwargs):
        self.command_manager = kwargs.get('command_manager')
        self.task_manager = kwargs.get('task_manager')
        self.message_sender = kwargs.get('message_sender')
        self.settings_manager = kwargs.get('settings_manager')
        self.storage_manager = kwargs.get('storage_manager')

    def load_all(self, extensions):
        for extension in extensions:
            settings = extensions[extension]
            if not 'disabled' in settings:
                self.load(extension)

    def is_loaded(self, name):
        for extension in self.extensions:
            if extension['name'] == name:
                return True
        return False

    def load(self, name):
        print('[ExtensionManager] Loading extension: ' + name)

        try:
            # Import the extension
            extension_module = importlib.import_module('.'+name, 'extensions')

            # Get extension settings
            settings = self.settings_manager.get_extension(name)

            # Get extension storage
            storage = Storage(self.storage_manager, name)

            # Run the extension init function
            extension = getattr(extension_module, name.capitalize())(
                message_sender = self.message_sender,
                settings = settings,
                storage = storage
            )

            # Add extension to list of extensions
            self.extensions.append({'name': name, 'extension': extension})

            # Add commands to command manager
            for command in extension.get_commands():
                self.command_manager.add(name, command)

            # Add tasks to task manager
            for task in extension.get_tasks():
                self.task_manager.add(name, task)

            print('[ExtensionManager] Extension loaded: ' + name)
            return True
        except Exception as e:
            print('[ExtensionManager] Error loading ' + name + ': ' + str(e))
            print(traceback.format_exc())

        return False

    def unload(self, name):
        print('[ExtensionManager] Unloading extension: ' + name)

        try:
            # Remove extension from list of extensions
            for extension in self.extensions:
                if extension['name'] == name:
                    self.extensions.remove(extension)
                    break

            # Remove commands from command manager
            self.command_manager.remove_extension(name)

            # Remove tasks from task manager
            self.task_manager.remove_extension(name)

            # Remove module from python cache (so the file gets re-read from disk)
            if 'extensions.'+name in sys.modules:
                del sys.modules['extensions.' + name]

            print('[ExtensionManager] Extension unloaded: ' + name)
            return True
        except Exception as e:
            print('[ExtensionManager] Error unloading ' + name + ': ' + str(e))
        
        return False

    def handle(self, _type, name, command):
        for entry in self.extensions:
            if entry['name'] == name:
                getattr(entry['extension'], _type)(command)
