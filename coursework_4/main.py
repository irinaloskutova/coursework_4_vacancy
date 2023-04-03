from classes import *

def main():
    while True:
        vacancy = input("Введите ключевое слово по которому будем искать вакансии: ")
        if not vacancy.isalpha():
            print('Ой, что-то пошло не так. Наверное, Вы ввели не слово.')
            print('Вы хотите продолжить поиск?')
            print('Пожалуйста, напишите "да" или "нет".')
            answer = input()
            if answer.isalpha() and answer.lower() == 'да':
                continue
            elif not answer.isalpha() or answer.lower() == 'нет':
                exit('Возвращайтесь в любое время.')
        else:
            print('Ищем для Вас вакансии')
            sj_vac = SJVacancy(vacancy)
            sj_vac.to_json()
            print("Очень сильно ищем...")
            hh_vac = HHVacancy(vacancy)
            hh_vac.to_json()
            print("Ждать уже совсем чуть-чуть...")
            all_vac = Vacancy(vacancy)
            all_vac.combine_json()
        con = Connector('all_vacancy.json')
        mix = CountMixin('all_vacancy.json')
        count_vacancy = mix.get_count_of_vacancy
        while True:
            if count_vacancy <= 0:
                exit("Вакансий не нашлось, программа закрыта. Попробуйте поискать вакансию по другому ключевому слову")
            else:
                print(f"Мы нашли для Вас {count_vacancy} вакансий")
                count = input("Напишите количество вакансий, которые мы выведем на экран? ")
                if not count.isdigit() or int(count) <= 0 or int(count) > count_vacancy:
                    print(f"Давайте попробуем еще раз. Введите любое целое число больше ноля и "
                          f"меньше {count_vacancy}: ")
                    continue
                else:
                    sorted_vacancy = con.sort_salary()
                    items = []
                    for i in range(int(count)):
                        vac = Vacancy_list(sorted_vacancy[i]['source'], sorted_vacancy[i]['name'], sorted_vacancy[i]['url'],
                                      sorted_vacancy[i]['city'], sorted_vacancy[i]['requirement'], sorted_vacancy[i]['currency'],
                                      sorted_vacancy[i]['salary_from'], sorted_vacancy[i]['salary_to'])
                        items.append(vac)
                        print(vac)
                    break

        print('Спасибо, что воспользовались нашим поиском. \nВозвращайтесь в любое время.')
        break


if __name__ == '__main__':
    main()
