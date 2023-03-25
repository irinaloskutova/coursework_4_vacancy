import collections
import json
from abc import ABC, abstractmethod
import os


import requests
from poetry.console.commands import self


class Engine(ABC):
    @abstractmethod
    def get_request(self):
        pass

    @staticmethod
    def get_connector(file_name):
        """Возвращает экземпляр класса Connector """
        return file_name
        pass


class HH(Engine):
    def __init__(self, data):
        """Инициализирует класс где data - название по которому будет происходить поиск"""
        self.data = data
        self.request = self.get_request()

    def get_request(self):
        """Возвращает вакансии с сайта HeadHunter"""
        vacancies = []
        for page in range(1, 11):
            params = {
                "text": f"{self.data}",
                "area": 113,
                "page": page,
                "per_page": 100,
            }
            vacancies.extend(requests.get('https://api.hh.ru/vacancies', params=params).json()["items"])
        return vacancies


class Superjob(Engine):
    def __init__(self, data):
        """Инициализирует класс где data - название по которому будет происходить поиск"""
        self.data = data
        self.request = self.get_request()

    def get_request(self):
        """Возвращает вакансии с сайта SuperJob"""
        url = "https://api.superjob.ru/2.0/vacancies/"
        params = {'keyword': self.data, "count": 1000}
        my_auth_data = {"X-Api-App-Id": os.environ['SuperJob_api_key']}
        response = requests.get(url, headers=my_auth_data, params=params)
        vacancies = response.json()
        return vacancies

