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

    def __init__(self, data: str):
        """Инициализирует класс где data - название по которому будет происходить поиск"""
        self.data = data
        self.request = self.get_request()

    def get_request(self):
        """Возвращает 1000 вакансий с сайта HeadHunter"""
        try:
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
        except requests.exceptions.ConnectTimeout:
            print('Oops. Connection timeout occured!')
        except requests.exceptions.ReadTimeout:
            print('Oops. Read timeout occured')
        except requests.exceptions.ConnectionError:
            print('Seems like dns lookup failed..')
        except requests.exceptions.HTTPError as err:
            print('Oops. HTTP Error occured')
            print('Response is: {content}'.format(content=err.response.content))


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
            if self.request[i]['snippet']['requirement'] is not None:
                s = self.request[i]['snippet']['requirement']
                for x, y in ("<highlighttext>", ""), ("</highlighttext>", ""):
                    s = s.replace(x, y)
            info = {
                'source': 'HeadHunter',
                'name': self.request[i]['name'],
                'city': "(Город не указан)" if (self.request[i]['address']) == None else self.request[i]['address']['city'],
                'salary_from': 0.0 if (self.request[i]['salary'] == None or self.request[i]['salary']['from'] == 0 or
                                       self.request[i]['salary']['from'] == None) else self.request[i]['salary']['from'],
                'salary_to': "(Предельная зарплата не указана)" if (self.request[i]['salary'] == None or
                             self.request[i]['salary']['to'] == None) else self.request[i]['salary']['to'],
                'currency': "(Валюта не указана)" if self.request[i]['salary'] == None else f"{self.request[i]['salary']['currency']}",
                'url': self.request[i]['alternate_url'],
                "requirement": s,
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
        try:
            list_vacancy = []
            for i in range(len(self.request)):
                info = {
                    'source': 'SuperJob',
                    'name': self.request[i]['profession'],
                    'city': "(Город не указан)" if self.request[i]['town'] == None else self.request[i]['town']['title'],
                    'salary_from': 0.0 if self.request[i]['payment_from'] == 0 else self.request[i]['payment_from'],
                    'salary_to': "(Предельная зарплата не указана)" if (self.request[i]['payment_to'] == 0 or self.request[i]['payment_to'] ==
                                                  None) else self.request[i]['payment_to'],
                    'currency': "(Валюта не указана)" if self.request[i]['currency'] == None else self.request[i]['currency'],
                    "requirement": self.request[i]['candidat'],
                    'url': self.request[i]['link'],
                }
                list_vacancy.append(info)
            return list_vacancy
        except Exception:
            print("Error")
        else:
            print("Выполняем поиск на сайте SuperJob")

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
        Проверяет, что файл существует, если нет то выбрасывает исключение.
        Возвращает переменную с данными
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

    def sort_salary(self):
        with open(self.__data_file, 'r', encoding='UTF-8') as f:
            data = json.load(f)
        sorted_data = sorted(data, key=lambda x: x["salary_from"], reverse=True)
        return sorted_data

