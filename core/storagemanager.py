import os
import json
import time
import threading

class StorageManager:

    # Flag to check whether the storage has to be flushed to filesystem
    changed = False

    def __init__(self, file_name):
        self.file_name = file_name

        if not os.path.isfile(file_name):
            print('[StorageManager] Storage file does not exists yet, creating new: ' + self.file_name)
            json.dump({}, open(self.file_name, 'w'))

        if not self.load():
            print('[StorageManager] Fatal error, could not load ' + self.file_name)
            return
            
        worker = threading.Thread(target=self.worker)
        worker.start()
    
    def load(self):
        try:
            print('[StorageManager] Reading storage from ' + self.file_name)
            self.storage = json.load(open(self.file_name))
            return True
        except Exception as e:
            print('[StorageManager] Error loading ' + self.file_name)
        return False

    def get(self, name):
        if not name in self.storage:
            print('[StorageManager] Creating empty storage for ' + name)
            self.storage[name] = {}

        return self.storage[name]
    
    def save(self):
        try:
            print('[StorageManager] Saving storage to ' + self.file_name)
            json.dump(self.storage, open(self.file_name, 'w'))
        except Exception as e:
            print('[StorageManager] Error saving to ' + self.file_name)
        return False

    def worker(self):
        print('[StorageManager-Worker] Created')
        while True:

            if self.changed:
                try:
                    self.changed = False
                    self.save()
                except Exception as e:
                    print('[StorageManager-Worker] Error while saving: ' + str(e))

            time.sleep(5)

    '''
    Get storage for extension
    '''
    def get_extension(self, name):
        storage = {}

        if not name in self.storage:
            print('[StorageManager] Creating storage entry for ' + name)
            self.storage[name] = {}

        return self.storage[name]

class Storage:

    def __init__(self, storage_manager, extension):
        print('[StorageManager] Created')
        self.__storage_manager = storage_manager
        self.storage = storage_manager.get(extension)

    def exists(self, name):
        return name in self.storage

    def get(self, name):
        return self.storage[name]

    def delete(self, name):
        if name in self.storage:
            del self.storage[name]
            self.__storage_manager.changed = True

    def put(self, name, value):
        self.storage[name] = value
        self.__storage_manager.changed = True
