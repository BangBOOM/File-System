"""
author:Wenquan Yang
time:2020/6/16 0:35
"""
import hashlib


def md5(text: str):
    m = hashlib.md5()
    m.update(text.encode("utf-8"))
    return m.hexdigest()


class User:
    def __init__(self, name, password, user_id):
        self._name = name
        self._password = md5(password)
        self._user_id = user_id

    @property
    def user_id(self):
        return self._user_id

    @property
    def name(self):
        return self._name

    def login(self, name, password, root_user=False):
        return name == self._name and (root_user or md5(password) == self._password)

    def __str__(self):
        print(self.name, self.user_id, self._password)
