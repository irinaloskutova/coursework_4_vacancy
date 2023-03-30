import collections
import json
from abc import ABC, abstractmethod
import os
from functools import reduce

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

    def __init__(self, data: str):
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
    """Возвращает вакансии с сайта SuperJob"""

    def __init__(self, data: str):
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
            info = {
                'source': 'SuperJob',
                'name': self.request[i]['profession'],
                'city': None if self.request[i]['town'] == None else self.request[i]['town']['title'],
                'salary': {
                    'from': None if self.request[i]['payment_from'] == 0 else f"{self.request[i]['payment_from']} "
                                                                              f"{None if self.request[i]['currency'] == 0 else self.request[i]['currency']}",
                    'to': None if self.request[i]['payment_to'] == 0 else f"{self.request[i]['payment_to']} "
                                                                          f"{None if self.request[i]['currency'] == 0 else self.request[i]['currency']}",
                },
                "requirement": self.request[i]['candidat'],
                'url': self.request[i]['link'],
            }
            list_vacancy.append(info)
        return list_vacancy

    def to_json(self):
        with open('sjvacancy.json', 'w') as f:
            json.dump(self.get_vacancy, f, indent=2)


class Vacancy(HHVacancy, SJVacancy):
    """Собирает все найденные ранее вакансии в один json файл"""

    def combine_json(self):
        a = json.loads(open('hhvacancy.json').read())
        b = json.loads(open('sjvacancy.json').read())
        c = a + b
        with open('all_vacancy.json', 'w') as f:
            json.dump(c, f, indent=2)


class CountMixin:
    """Подсчитывает количество вакансий от указанного сервиса """
    def __init__(self, data: str):
        self.data = data

    @property
    def get_count_of_vacancy(self):
        try:
            with open(f'{self.data}', 'r') as f:
                data = json.load(f)
                return len(data)
        except FileNotFoundError:
            print("FileNotFoundError")


class Connector:
    """
    Класс коннектор к файлу, обязательно файл должен быть в json формате
    не забывать проверять целостность данных, что файл с данными не подвергся
    внешней деградации
    """
    __data_file = None

    def __init__(self, file_path: str):
        self.__data_file = file_path

    @property
    def data_file(self):
        return self.__data_file

    @data_file.setter
    def data_file(self, value: str):
        self.__data_file = value

    def connect(self):
        """
        Проверяет, что файл существует, если нет то выбрасывает исключение. Возвращает переменную с данными
        """
        if not os.path.isfile(self.__data_file):
            raise FileNotFoundError(f"Файл {self.__data_file} отсутствует")
        try:
            with open(self.__data_file, 'r', encoding='UTF-8') as file:
                json_reader = json.load(file)
                for i in json_reader:
                    if i.get('name') == 0:
                        print('Something wrong')
                    else:
                        return json_reader
                return json_reader
        except Exception:
            print(f'Файл {self.__data_file} поврежден')

    def insert(self, data: str):
        """
        Запись данных в файл с сохранением структуры и исходных данных
        """
        with open(f"{self.__data_file}", 'w+', encoding="UTF-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def select(self, query):
        """
        Выбор данных из файла с применением фильтрации
        query содержит словарь, в котором ключ это поле для
        фильтрации, а значение это искомое значение, например:
        {'price': 1000}, должно отфильтровать данные по полю price
        и вернуть все строки, в которых цена 1000
        """
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
    # req_1 = HHVacancy("python")
    # print(req_1.get_vacancy)
    # vac_1 = CountMixin(req_.get_request())
    # req_2 = Superjob('python')
    # req_2 = SJVacancy("python")
    # print(req_2.get_vacancy)
    # print(req_2.get_info())
    # req_1.to_json()
    # req_2.to_json()
    # con = Connector('hhvacancy.json')
    # print(con.connect())
    mix = CountMixin()
