import re

class CommandManager:

    commands = {}

    '''
    Add command
    '''
    def add(self, extension, command):
        if not extension in self.commands:
            self.commands.update({extension: []})

        new_command = {
            'extension': extension,
            'description': command.get('description')
        }

        if 'pattern' in command:
            pattern = command.get('pattern')
            new_command.update({'pattern': pattern})
            print('[CommandManager] Added command for '+extension+': '+pattern)
        else:
            prefix = command.get('prefix')
            new_command.update({'prefix': prefix})
            print('[CommandManager] Added command for '+extension+': '+prefix)

        self.commands[extension].append(new_command)


    '''
    Return all commands in a list
    '''
    def get_all_commands(self):
        for extension in self.commands:
            for command in self.commands[extension]:
                yield command


    '''
    Remove all commands from an extension
    '''
    def remove_extension(self, extension):
        if extension in self.commands:
            del self.commands[extension]


    '''
    Get extension that is responsible for the command
    '''
    def get_extension(self, text):
        for command in self.get_all_commands():
            if 'pattern' in command:
                if re.search(command['pattern'], text):
                    return command['extension']
            else:
                if text.startswith(command['prefix']):
                    return command['extension']
        return None
