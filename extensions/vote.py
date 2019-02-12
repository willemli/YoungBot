import telepot
import time
import json
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

class Vote:

    # Not active
    votes_in_creation = {}

    # Active
    '''
    active_votes = {
        1337: {
            'title': 'TTTTTTTTTTTT',
            'limit': 1,
            'options': {
                'HELLO': [251, 9]
            }
        }
    }
    '''
    active_votes = {}



    def __init__(self, **kwargs):
        self.message_sender = kwargs.get('message_sender')
        self.settings = kwargs.get('settings')

    def get_commands(self):
        return [
            {'prefix': '/vote', 'description': 'Display help for vote'},
        ]


    def get_tasks(self):
        return []

    def chat(self, message):
        content_type, chat_type, chat_id = telepot.glance(message)
        user_id = message['from']['id']

        command = ''

        message_split = message['text'].split(' ')
        if len(message_split) > 1:
            command = message_split[1]
        
        # Help
        if command == '':
            print(self.votes_in_creation)
            print(self.active_votes)
            self.message_sender.enqueue({
                'chat_id': chat_id,
                'text': '<b>Vote bot</b>\n\nstart [title] | start a vote\n\nadd [comma seperated] | Add entries in vote\n\nlimit | Set limit for amount of votes\n\ndone | Publish vote\n\ncancel | Cancel new vote'
            })

        # Commands for vote not in progress
        if not user_id in self.votes_in_creation:
            if command == 'start':
                title = message['text'][11:].strip() 

                # sir pls
                if title == '':
                    self.message_sender.enqueue({
                        'chat_id': chat_id,
                        'text': '<b>sir pls enter title sir</b>'
                    })
                    return

                # Send user message
                self.votes_in_creation.update({
                    user_id: {
                        'title': title,
                        'limit': 1,
                        'options': {}
                    }
                })
                self.message_sender.enqueue({
                    'chat_id': chat_id,
                    'text': '<b>Started vote</b> ' + title
                })

        # Commands for vote in progress
        else:
            if command == 'add':
                options = message['text'][9:].strip()
                options_split = options.split(',')
                text = ''
                for option in options_split:
                    option = option.strip()
                    self.votes_in_creation[user_id]['options'].update({option: []})
                    text += '<b>Added option: </b>' + option + '\n'

                self.message_sender.enqueue({
                    'chat_id': chat_id,
                    'text': text
                })
            elif command == 'limit':
                limit = int(message['text'][11:].strip())
                self.votes_in_creation[user_id]['limit'] = limit
                self.message_sender.enqueue({
                    'chat_id': chat_id,
                    'text': '<b>Limit: </b>' + str(limit)
                })
            elif command == 'done':
                vote = self.votes_in_creation[user_id]
                vote_id = message['message_id']

                # Delete from progress
                self.votes_in_creation.pop(user_id)

                # Add to active
                self.active_votes.update({vote_id: vote})

                # Display to user
                self.update_vote_progress(chat_id, vote_id)
            elif command == 'cancel':
                self.votes_in_creation.pop(user_id)
                self.message_sender.enqueue({
                    'chat_id': chat_id,
                    'text': 'Vote cancelled'
                })
    

    '''
    {
        "_":"vote",
        "vote_id":9538,
        "option":2
    }
    '''
    def callback(self, message):
        print('[Vote] ====================================')
        print(message)
        print('[Vote] ====================================\n')

        user_id = message['from']['id']
        chat_id = message['message']['chat']['id']

        data = json.loads(message['data'])
        vote_id = data['vote_id']
        option = int(data['option'])

        if not self.is_valid_vote(user_id, vote_id, option):
            print('[Vote] Not a valid vote')
            return

        options = self.active_votes[vote_id]['options']

        # Current option in string
        current_option = self.get_current_option(user_id, vote_id)

        # New vote title in string
        vote_title = self.dict_key_from_index(options, option)

        # If the user has voted already
        if current_option:
            # If vote is different, apply new vote
            if current_option is not vote_title:
                self.remove_vote(user_id, vote_id)
                options[vote_title].append(user_id)
                self.message_sender.answerCallbackQuery(message['id'], '🇰🇷 Vote edited')

            # Vote is same, remove
            else:
                self.remove_vote(user_id, vote_id)
                self.message_sender.answerCallbackQuery(message['id'], '🇰🇷 Vote removed')
        else:
            # Apply the vote
            options[vote_title].append(user_id)
            self.message_sender.answerCallbackQuery(message['id'], '🇰🇷 Vote Added')
            
        self.update_vote_progress(chat_id, vote_id)
        
    
    def remove_vote(self, user_id, vote_id):
        for option in self.active_votes[vote_id]['options']:
            user_ids = self.active_votes[vote_id]['options'][option]
            if user_id in user_ids:
                user_ids.remove(user_id)
                print('removed!')
    

    '''
    Returns the current option (string) of the user
    None if not applicable
    '''
    def get_current_option(self, user_id, vote_id):
        options = self.active_votes[vote_id]['options']
        for key, value in options.items():
            if user_id in value:
                return key
        return None

    def is_valid_vote(self, user_id, vote_id, option):
        # Check if vote_id is valid
        if not vote_id in self.active_votes:
            print(str(vote_id) + ' is not valid')
            return False

        # Check if option is valid
        if not (option > -1 and option < len(self.active_votes[vote_id]['options'])):
            print(str(option) + ' not in range')
            return False

        return True

    def update_vote_progress(self, chat_id, vote_id):
        vote = self.active_votes[vote_id]
        title = vote['title']
        options = vote['options']
        limit = vote['limit']
        '''
        active_votes = {
            1337: {
                'title': 'TTTTTTTTTTTT',
                'limit': 1,
                'options': {
                    'HELLO': [251, 9]
                },
                OPTIONAL -- 'msg_identifier'
            }
        }
        '''
        text = '<b>'+title+'</b>\n\n'
        text += str(self.count_votes(vote_id))+'/'+str(limit)+' votes'
        print(text)

        inline_keyboards = []

        # Set inline keyboards
        for index, option in enumerate(options):
            inline_keyboards.append(
                [InlineKeyboardButton(
                    text = option, 
                    callback_data = json.dumps({'_': 'vote', 'vote_id': vote_id, 'option': index})
                )]
            )
        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboards)
        

        # Check if new message needs to be sent or edit
        if 'msg_identifier' in vote:
            msg_identifier = vote['msg_identifier']

            # Check if voting is finished
            if self.count_votes(vote_id) == limit:
                text += '\n\n'
                for key, value in self.active_votes[vote_id]['options'].items():
                    text += '<b>['+str(len(value))+']</b> '+key+'\n'
                keyboard = None

            self.message_sender.send({
                'msg_identifier': msg_identifier,
                'type': 'edit',
                'text': text,
                'reply_markup': keyboard
            })
        else:
            outgoing_message = self.message_sender.send({
                'chat_id': chat_id,
                'text': text,
                'reply_markup': keyboard
            })
            vote.update({'msg_identifier': telepot.message_identifier(outgoing_message)})
        
        

    
    def count_votes(self, vote_id):
        vote = self.active_votes[vote_id]
        options = vote['options']
        total_votes = 0
        for votes in options:
            for user_id in options[votes]:
                total_votes += 1
        return total_votes
    
    def dict_key_from_index(self, dictionary, index):
        current_index = 0
        for key, value in dictionary.items():
            if index == current_index:
                return key
            current_index += 1
        return None