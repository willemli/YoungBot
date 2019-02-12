import threading
import time

'''
Handles all things related to tasks 
(extension specified actions at specific intervals)
'''
class TaskManager:

    tasks = {}

    def __init__(self, **kwargs):
        print('[TaskManager] Created')


    '''
    Starts the task manager
    '''
    def start(self):
        task_manager_thread = threading.Thread(target=self.task_manager)
        task_manager_thread.start()
        

    '''
    Set the extension manager
    '''
    def set_extension_manager(self, extension_manager):
        self.extension_manager = extension_manager


    '''
    Add a task
    '''
    def add(self, extension, task):
        name = task.get('name')
        interval = task.get('interval')

        if not extension in self.tasks:
            self.tasks.update({extension: []})

        self.tasks[extension].append({
            'extension': extension,
            'name': name,
            'interval': interval,
            'last_executed': time.time()
        })
        print('[TaskManager] Added task for '+extension+': '+name + ' ('+str(interval)+')')


    '''
    Return all tasks in a list
    '''
    def get_all_tasks(self):
        for extension in self.tasks:
            for task in self.tasks[extension]:
                yield task


    '''
    Remove all tasks from an extension
    '''
    def remove_extension(self, extension):
        if extension in self.tasks:
            del self.tasks[extension]


    '''
    Task Manager thread
    Runs every 500ms
    '''
    def task_manager(self):
        while True:
            current_time = time.time()

            for task in self.get_all_tasks():
                if current_time > (task['last_executed'] + task['interval']):
                    
                    extension = task['extension']
                    name = task['name']

                    print('[TaskManager] Starting task '+name+' for '+extension)

                    task_thread = threading.Thread(target=self.extension_manager.handle, args=('task', extension, name))
                    task_thread.start()

                    task['last_executed'] = current_time

            time.sleep(0.5)
