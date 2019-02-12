import json

class SettingsManager:

    def __init__(self, file_name):
        self.file_name = file_name
        self.load()
    
    def load(self):
        print('[SettingsManager] Reading settings from ' + self.file_name)
        self.settings = json.load(open(self.file_name))

    def get(self, name):
        return self.settings[name]
    
    '''
    Get settings for extension
    Adds global settings
    '''
    def get_extension(self, name):
        # To return
        settings = {}

        # If there are no settings for the extension
        # Print warning and return empty
        if not name in self.settings['extensions']:
            print('[SettingsManager] Warning: no entry for ' + name + ' in settings!')
            return {}

        # Extension settings as specified
        extension_settings = self.settings['extensions'][name]

        # Include all global variables
        if 'global_settings' in extension_settings:
            global_settings = extension_settings['global_settings']
            for global_setting in global_settings:
                settings.update({global_setting: self.settings[global_setting]})

        # Add all extension settings
        for key, value in extension_settings.items():
            if key != 'global_settings':
                settings.update({key: value})

        return settings
