from nice_printers import info
from time import time
import os
import pickle


class CacheStorage:
    def __init__(self, params):
        self.filename = params['cache_filename']
        self.filepath = os.path.join(os.getcwd(), self.filename)
        # (name, type): [(answer, add_time)]
        self.storage = {}
        if os.path.exists(self.filepath):
            self.load()

    def save(self):
        with open(self.filepath, 'wb') as f:
            pickle.dump(self.storage, f)

    def load(self):
        with open(self.filepath, 'rb') as f:
            load = pickle.load(f)
            clear_keys = []
            for key in load.keys():
                for entity in load[key]:
                    if entity[0]['Ttl'] + entity[1] < time():
                        clear_keys.append(key)
                        break
            for key in clear_keys:
                load.pop(key)
            self.storage = load

    def get_entity(self, parsed_data):
        result = []
        for question in parsed_data[1]:
            entity = self.storage.get((question['Name'], question['Type']))
            if entity is not None:
                for answer in entity:
                    if answer[0]['Ttl'] + answer[1] > time():
                        answer[0]['Ttl'] = answer[1] + answer[0]['Ttl'] - time()
                        result.append(answer[0])
        if result:
            info('Found cache entity')
            return result
        else:
            info('Nothing found :(')
            return None

    def put_entity(self, parsed_data):
        for answer_section in parsed_data[2:]:
            for answer in answer_section:
                if len(answer['Address']) == 0 or answer['Type'] > 2:
                    continue
                entity = self.storage.get((answer['Name'], answer['Type']))
                if entity is None:
                    self.storage.update({(answer['Name'], answer['Type']): [(answer, time())]})
                    info('Cache entity was created!')
                else:
                    entity.append((answer, time()))
                    info('Cache was updated')
