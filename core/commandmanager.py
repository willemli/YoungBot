class CommandManager:

    commands = {}

    '''
    Add command
    '''
    def add(self, extension, command):
        prefix = command.get('prefix')
        description = command.get('description')

        if not extension in self.commands:
            self.commands.update({extension: []})

        self.commands[extension].append({
            'extension': extension,
            'prefix': prefix,
            'description': description
        })

        print('[CommandManager] Added command for '+extension+': '+prefix)


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
            if text.startswith(command['prefix']):
                return command['extension']
        return None
