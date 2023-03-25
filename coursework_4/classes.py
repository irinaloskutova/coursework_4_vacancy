import collections
import json
from abc import ABC, abstractmethod
import os


import requests



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
    """Возвращает 1000 вакансий с сайта HeadHunter"""
    def __init__(self, data):
        """Инициализирует класс где data - название по которому будет происходить поиск"""
        self.data = data
        self.request = self.get_request()

    def get_request(self):
        """Возвращает 1000 вакансий с сайта HeadHunter"""
        vacancies = []
        for page in range(1, 11):
            params = {
                "text": f"{self.data}",
                "area": 113,
                "page": page,
                "per_page": 1,
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
        params = {'keyword': self.data, "count": 10000}
        my_auth_data = {"X-Api-App-Id": os.environ['SuperJob_api_key']}
        response = requests.get(url, headers=my_auth_data, params=params)
        vacancies = response.json()
        return vacancies

class HHVacancy(HH):
    """ HeadHunter Vacancy """
    def get_vacancy(self):
        """Взяли все ранее найденные вакансии с HeadHunter и записали их в переменную с полями: наименование вакансии,
        город, зарплатная вилка, описание требований и url вакансии"""
        list_vacancy = []
        for i in range(len(self.request)):
            info = {
                'name': self.request[i]['name'],
                'city': None if self.request[i]['address'] == None else self.request[i]['address']['city'],
                'salary': {
                    'from': None if self.request[i]['salary'] == 0 else self.request[i]['salary']['from'],
                    'to': None if self.request[i]['salary'] == 0 else self.request[i]['salary']['to'],
                },
                "requirement": self.request[i]['snippet']['requirement'],
                'url': self.request[i]['alternate_url'],
            }
            list_vacancy.append(info)
        return list_vacancy

class SJVacancy(Superjob):
    """ SuperJob Vacancy """
    def get_info(self):
        """Взяли все ранее найденные вакансии с HeadHunter и записали их в переменную с полями: наименование вакансии,
        город, зарплатная вилка, описание требований и url вакансии"""
        list_vacancy = []
        for i in range(len(self.request)+1):
            print(i)
            info = {
                'name': self.request['objects'][i]['profession'],
                'city': None if self.request[i]['town'] == None else self.request[i]['town']['title'],
                'salary': {
                    'from': None if self.request['objects'][i]['payment_from'] == 0 else self.request['objects'][i]['payment_from'],
                    'to': None if self.request['objects'][i]['payment_to'] == 0 else self.request['objects'][i]['payment_to'],
                },
                "requirement": self.request['objects'][i]['candidat'],
                'url': self.request['objects'][i]['link'],
            }
            list_vacancy.extend(info)
        return list_vacancy
