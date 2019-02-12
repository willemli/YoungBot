import threading


class WorkersManager:

    '''
    workers = [
        {'user_id': 3123123, 'worker': worker}
    ]
    '''
    workers = []


    def __init__(self, extension_manager):
        print('[WorkersManager] Created')

        self.extension_manager = extension_manager

    '''
    Creates a new worker
    '''
    def create_worker(self, user_id, _type, extension_name, message):
        self.remove_worker(user_id)

        worker = threading.Thread(target=self.extension_manager.handle, args=(_type, extension_name, message))
        worker.start()
        self.workers.append({'user_id': user_id, 'worker': worker})

    '''
    Removes a worker
    Make sure the worker is not alive!
    '''
    def remove_worker(self, user_id):
        for entry in self.workers:
            if entry['user_id'] == user_id:
                self.workers.remove(entry)

    def worker_is_available(self, user_id):
        for entry in self.workers:
            if entry['user_id'] == user_id:
                return not entry['worker'].is_alive()
        return True
