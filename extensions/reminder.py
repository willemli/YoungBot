import telepot
from datetime import datetime, date
from datetime import timedelta
from dateutil import parser
import json


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


class Reminder:

    def __init__(self, **kwargs):
        self.message_sender = kwargs.get('message_sender')
        self.settings = kwargs.get('settings')
        self.storage = kwargs.get('storage')

        if not self.storage.exists('reminders'):
            self.storage.put('reminders', json.dumps([]))

    def get_commands(self):
        return [
            {'prefix': '/remind', 'description': 'give me a reminder at a specific time'}
        ]

    def get_tasks(self):
        return [
            {
                'name': 'send_reminder',
                'interval': 35
            }
        ]

    def task(self, name):
        to_delete = []
        reminders = json.loads(self.storage.get('reminders'))

        for i, reminder in enumerate(reminders):
            if parser.parse(reminder['date']) <= datetime.now() and reminder['send'] == False:
                chat_id = reminder['chat_id']
                self.message_sender.enqueue({'chat_id': chat_id,
                                             'text': '<b>Reminder</b>\n\n' + reminder['reminder']
                                             })
                reminder['send'] = True
                to_delete.append(reminder)
        for r in to_delete:
            reminders.remove(r)
        self.storage.put('reminders', json.dumps(reminders, default=json_serial))

    def chat(self, message):

        content_type, chat_type, chat_id = telepot.glance(message)

        messageText = message['text']

        if messageText == '/remind':
            self.message_sender.enqueue({'chat_id': chat_id,
                                         'text': '<b>Reminder Bot</b>\n\n[Date] [Time] [Reminder]'
                                         })
        elif messageText == '/remind show':
           self.show(chat_id)
        elif messageText.startswith('/remind'):
            try:
                code = messageText.split('/remind ')[1]
                splitted = code.split(' ')
                date_str = splitted[0]
                time = splitted[1]
                reminder = splitted[2]
                for i in range(3, len(splitted)):
                    reminder += ' ' + str(splitted[i])

                date = self.get_date(date_str, time)

                if date == False:
                    self.message_sender.enqueue({'chat_id': chat_id,
                                                 'text': '<b>Error</b>\n\nPlease enter the date and time in the following format: \n\nDate Time'
                                                 })

                if date < datetime.now():
                    self.message_sender.enqueue({'chat_id': chat_id,
                                                 'text': '<b>Error</b>\n\nYou cannot add reminders in the past'
                                                 })
                    return

                reminders = json.loads(self.storage.get('reminders'))

                reminders.append({'date': date, 'reminder': reminder, 'chat_id': chat_id, 'send': False})

                self.storage.put('reminders', json.dumps(reminders, default=json_serial))
                self.message_sender.enqueue({'chat_id': chat_id,
                                             'text': '<b>Successfully added reminder</b>\n\n' + str(date) + '\n\n' + reminder
                                                     })
            except Exception as e:
                print(e)
                self.message_sender.enqueue({'chat_id': chat_id,
                                             'text': '<b>Error</b>\n\nPlease enter the reminder in the following format: \n\n/remind Date Time Reminder'
                                             })

    def get_date(self, date, time):
        try:
            if 'today' in date:
                return parser.parse(time)
            if 'tommorow' in date:
                return parser.parse(time) + timedelta(days=1)
            else:
                return parser.parse(date + ' ' + time)
        except Exception as e:
            return False

    def show(self, chat_id):
        res = []
        reminders = json.loads(self.storage.get('reminders'))

        for r in reminders:
            if r[2] == chat_id:
                res.append(r)

        res.sort(key=lambda x: x[0])

        msg = '<b>Reminders</b>\n\n'

        if len(res) == 0:
            msg += 'You have no reminders set'
            self.message_sender.enqueue({'chat_id': chat_id,
                                     'text': msg
                                     })
            return

        for r in res:
            msg += str(r[0]) + ' '  + r[1]
            msg += '\n'

        self.message_sender.enqueue({'chat_id': chat_id,
                                     'text': msg
                                     })