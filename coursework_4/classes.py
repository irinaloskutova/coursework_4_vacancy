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
        params = {'keyword': self.data, "count": 1000}
        my_auth_data = {"X-Api-App-Id": os.environ['SuperJob_api_key']}
        response = requests.get(url, headers=my_auth_data, params=params)
        vacancies = response.json()['objects']
        return vacancies

class HHVacancy(HH):
    """ HeadHunter Vacancy """
    @property
    def get_vacancy(self):
        """Взяли все ранее найденные вакансии с HeadHunter и записали их в переменную с полями: наименование вакансии,
        город, зарплатная вилка, описание требований и url вакансии"""
        list_vacancy = []
        for i in range(len(self.request)):
            info = {
                'source': 'HeadHunter',
                'name': self.request[i]['name'],
                'city': None if self.request[i]['address'] == None else self.request[i]['address']['city'],
                'salary': {
                        'from': None if self.request[i]['salary'] == 0 else f"{self.request[i]['salary']['from']} "
                                                                            f"{self.request[i]['salary']['currency']}",
                        'to': None if self.request[i]['salary'] == 0 else f"{self.request[i]['salary']['to']} "
                                                                            f"{self.request[i]['salary']['currency']}",
                },
                "requirement": self.request[i]['snippet']['requirement'],
                'url': self.request[i]['alternate_url'],
            }
            list_vacancy.append(info)
        return list_vacancy

    def to_json(self):
        with open('hhvacancy.json', 'w') as f:
            json.dump(self.get_vacancy, f, indent=2)

class SJVacancy(Superjob):
    """ SuperJob Vacancy """
    @property
    def get_vacancy(self):
        """Взяли все ранее найденные вакансии с SuperJob и записали их в переменную с полями: наименование вакансии,
        город, зарплатная вилка, описание требований и url вакансии"""
        list_vacancy = []
        for i in range(len(self.request)):
            # print(self.request[i]['profession'])
            info = {
                'source': 'SuperJob',
                'name': self.request[i]['profession'],
                'city': None if self.request[i]['town'] == None else self.request[i]['town']['title'],
                'salary': {
                    'from': None if self.request[i]['payment_from'] == 0 else f"{self.request[i]['payment_from']} "
                                                                                f"{None if self.request[i]['currency'] ==0 else self.request[i]['currency']}",
                    'to': None if self.request[i]['payment_to'] == 0 else f"{self.request[i]['payment_to']} "
                                                                                f"{None if self.request[i]['currency'] ==0 else self.request[i]['currency']}",
                },
                "requirement": self.request[i]['candidat'],
                'url': self.request[i]['link'],
            }
            list_vacancy.append(info)
        return list_vacancy

    def to_json(self):
        with open('sjvacancy.json', 'w') as f:
            json.dump(self.get_vacancy, f, indent=2)

class Vacancy:
    __slots__ = ('name_vacancy', 'salary', 'requirement', 'url_vacancy')

    def __init__(self, name_vacancy=None, url_vacancy=None, requirement=None, salary=0):
        self.name_vacancy = name_vacancy.strip(' !@#`*&^?/)(')
        self.url_vacancy = url_vacancy
        self.requirement = requirement
        self.salary = salary

    def __repr__(self):
        return f"Вакансия {self.name_vacancy} с зарплатой от {self.salary} руб. находится по адресу: " \
               f"{self.url_vacancy}. Требования/Описание вакансии: {self.requirement}"

class CountMixin:
    def __init__(self, data):
        self.data = data

    def get_vacancy(self):
        with open("vacancy.json", "w") as f:
            json.dump(self.data, f, indent=4)

    @property
    def get_count_of_vacancy(self):
        """
        Вернуть количество вакансий от текущего сервиса.
        Получать количество необходимо динамически из файла.
        """
        with open("f1.json", 'r') as f:
            data = json.load(f)
        return data

class Connector:
    """
    Класс коннектор к файлу, обязательно файл должен быть в json формате
    не забывать проверять целостность данных, что файл с данными не подвергся
    внешней деградации
    """
    __data_file = None

    @property
    def data_file(self):
        pass

    @data_file.setter
    def data_file(self, value):
        # тут должен быть код для установки файла
        self.__connect()

    def __connect(self):
        """
        Проверка на существование файла с данными и
        создание его при необходимости
        Также проверить на деградацию и возбудить исключение
        если файл потерял актуальность в структуре данных
        """
        pass

    def insert(self, data):
        """
        Запись данных в файл с сохранением структуры и исходных данных
        """
        pass

    def select(self, request):
        """
        Выбор данных из файла с применением фильтрации
        query содержит словарь, в котором ключ это поле для
        фильтрации, а значение это искомое значение, например:
        {'price': 1000}, должно отфильтровать данные по полю price
        и вернуть все строки, в которых цена 1000
        """
        for key, value in request['items'][i].items():
            while i < len(request['items']):
                try: id = request['items'][i]["id"]
                except: id = None
                try: name = request['items'][i]["name"]
                except: name = None
                try: url = request['items'][i]["alternate_url"]
                except: url = None
                try: requirement = request['items'][i]["snippet"]['requirement']
                except: requirement = None
                try: salary = request['items'][i]["salary"]['from']
                except: salary = None
                try: apply_alternate_url = request['items'][i]["apply_alternate_url"]
                except: apply_alternate_url = None
                i = i + 1
                if name != None and requirement != None and salary != None and url != None:

                    dict_request = collections.Counter(name=name, requirement=requirement, salary=salary, vacancy_url=url,
                             response_vacancy=apply_alternate_url)
                    # list_request.append(dict(name=name, requirement=requirement, salary=salary, vacancy_url=url,
                    #          response_vacancy=apply_alternate_url))
                    # print(len(dict_request))
                    with open("f3.json", "a") as f:
                        json.dump(dict_request, f, indent=4)
                    return dict_request
        pass

    def delete(self, query):
        """
        Удаление записей из файла, которые соответствуют запрос,
        как в методе select. Если в query передан пустой словарь, то
        функция удаления не сработает
        """
        pass

if __name__ == '__main__':
    # req_ = HH("python")
    # vac1 = Superjob('python')
    # print(vac1.get_request())
    req_1 = HHVacancy("python")
    # print(req_1.get_vacancy)
    # vac_1 = CountMixin(req_.get_request())
    # req_2 = Superjob('python')
    req_2 = SJVacancy("python")
    # print(req_2.get_vacancy)
    # print(req_2.get_info())
    req_1.to_json()
    req_2.to_json()
