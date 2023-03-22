import collections
import json
from abc import ABC, abstractmethod


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
        """Берет 100 вакансий с HH.ru со страницы 0"""
        page_number = 0
        url = f"https://api.hh.ru/vacancies?text={self.data}&area=113&per_page=100&page="
        request = requests.get(f'{url}{int(page_number)}').json()
        return request


class Superjob(Engine):
    def get_request(self):
        pass

class Vacancy:
    __slots__ = ('name_vacancy', 'url_vacancy', 'requirement', 'salary')

    def __init__(self, name_vacancy=None, url_vacancy=None, requirement=None, salary=0):
        self.name_vacancy = name_vacancy.strip(' !@#`*&^?/)(')
        self.url_vacancy = url_vacancy
        self.requirement = requirement
        self.salary = salary

    def __repr__(self):
        return f"HH: Вакансия {self.name_vacancy} с зарплатой от {self.salary} руб. находится по адресу: " \
               f"{self.url_vacancy}. Требования: {self.requirement}"

# class CountMixin:
#     def __init__(self, data):
#         self.data = data
#
#     def get_vacancy(self):
#
#         # for k, v in HH.request.items():
#         #     print(k, v)
#         #     name_of_vacancy = HH.request['items'][i]['name']
#         #     while i < 20:
#         #         i += 1
#         #     return name_of_vacancy
#
#     @property
#     def get_count_of_vacancy(self):
#         """
#         Вернуть количество вакансий от текущего сервиса.
#         Получать количество необходимо динамически из файла.
#         """
#         with open("f1.json", 'r') as f:
#             data = json.load(f)
#         return data


class HHVacancy(Vacancy):  # add counter mixin
    """ HeadHunter Vacancy """

    def __str__(self):
        return f'HH: {self.name}, зарплата: {self.salary} руб/мес'

class SJVacancy(Vacancy):  # add counter mixin
    """ SuperJob Vacancy """

    def __str__(self):
        return f'SJ: {self.name}, зарплата: {self.salary} руб/мес'

    def sorting(vacancies):
        """ Должен сортировать любой список вакансий по ежемесячной оплате (gt, lt magic methods) """
        pass

    def get_top(vacancies, top_count):
        """ Должен возвращать {top_count} записей из вакансий по зарплате (iter, next magic methods) """
        pass


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
#     df = Connector('df.json')
#
#     data_for_file = {'id': 1, 'title': 'tet'}
#
#     df.insert(data_for_file)
#     data_from_file = df.select(dict())
#     assert data_from_file == [data_for_file]
#
#     df.delete({'id': 1})
#     data_from_file = df.select(dict())
#     assert data_from_file == []
#     a = CountMixin()
#     b = HH('python')
#
#     print(b.get_request())
    vac = Vacancy(" pop", "www", "lalalala", 10000)
    print(vac.__repr__())
