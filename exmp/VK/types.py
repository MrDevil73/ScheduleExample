import requests
import aiohttp
import asyncio
from ..logg import LoggEvent

MESSAGE_NEW = "message_new"
CALLBACK_UPDATE = "message_event"


class MessageVk:
    date = 0
    from_id = 0
    id = 0
    out = 0
    version = 0
    attachments = []
    conversation_message_id = 0
    fwd_messages = []
    important = None
    is_hidden = None
    peer_id = 0
    random_id = 0
    text = None
    payload = None

    def __init__(self, data):
        self.__dict__.update(data)


class Object:
    client_info = {}  # он мне не нужен
    message = MessageVk({})

    def __init__(self, data):
        self.client_info = data.get('client_info', {})
        self.message = MessageVk(data.get('message', {}))


class Event:
    event_id = None
    payload = None
    peer_id = 0
    user_id = 0
    conversation_message_id = 0

    def __init__(self, data):
        self.__dict__.update(data)


class Update:
    v = 0
    type = None
    event_id = None
    group_id = None

    def __init__(self, data):
        self.__dict__.update(data)
        if self.type == MESSAGE_NEW:
            self.object = Object(data.get('object', {}))
        elif self.type == CALLBACK_UPDATE:
            self.event = Event(data.get('object', {}))


class UserFromGet:
    def __init__(self, id, first_name, last_name, username):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username


class Bot:
    token = ""
    v = "5.199"

    def __init__(self, token, ver=v):
        self.token = token
        self.v = ver

    async def req(self, method_name, **params):
        try:
            url = f"https://api.vk.com/method/{method_name}"
            params['access_token'] = self.token
            params['v'] = self.v
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    pass
        except Exception as e:
            del params['access_token']
            LoggEvent("SYS", 4444, "sysError", f"VkAPI {method_name} {str(params)}")

    def user_get(self, id_user) -> UserFromGet:
        url = f"https://api.vk.com/method/users.get"
        params = {'access_token': self.token, 'v': self.v, 'user_ids': id_user, 'fields': 'domain'}
        js = requests.get(url, params=params).json()
        if js.get('response'):
            elem = js['response'][0]
            user = UserFromGet(elem['id'], elem['first_name'], elem['last_name'], elem['domain'])
            return user
        else:
            return None

    def users_get(self, ids_users):
        url = f"https://api.vk.com/method/users.get"
        params = {'access_token': self.token, 'v': self.v, 'user_ids': ",".join(map(str, ids_users[:500])), 'fields': 'domain'}
        js = requests.get(url, params=params)
        if js.status_code == 200:
            js_ = js.json()
            if js_.get('response', None):
                return js_['response']
            else:
                return []
        else:
            return []

    def send_message(self, **params):
        return self.req('messages.send', **params)

    def edit_message(self, **params):
        return self.req('messages.edit', **params)

    def delete_message(self, **params):
        return self.req('messages.delete', **params)
