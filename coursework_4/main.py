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
            # sj_vac = SJVacancy('python')  # (vacancy)
            sj_vac.to_json()  # в основной логике программы должны быть включены, чтоб динамически перезаписывались
            print("Очень сильно ищем...")
            hh_vac = HHVacancy(vacancy)
            # hh_vac = HHVacancy('python')  # (vacancy)
            hh_vac.to_json()  # в основной логике программы должны быть включены, чтоб динамически перезаписывались
            print("Ждать уже совсем чуть-чуть...")
            all_vac = Vacancy(vacancy)
            # all_vac = Vacancy('python')  # (vacancy)
            all_vac.combine_json()  # в основной логике программы должны быть включены, чтоб динамически перезаписывались
            con = Connector('all_vacancy.json')
            mix = CountMixin('all_vacancy.json')

        if mix.get_count_of_vacancy > 0:
            print(f"Мы нашли для Вас {mix.get_count_of_vacancy} вакансий")

        else:
            exit("Вакансий не нашлось, программа закрыта. Попробуйте поискать вакансию по другому ключевому слову")
        while True:
            count = input("Напишите количество вакансий, которые мы выведем на экран?")
            if not count.isdigit() or int(count) <= 0:
                print("Давайте попробуем еще раз. Введите любое целое число больше ноля: ")
                continue
            else:
                u = con.sort_salary()
                for i in range(int(count)):
                    print(f"\nНа сайте: {u[i]['source']} мы нашли вакансию: {u[i]['name']} \nс зарплатой от {u[i]['salary_from']} "
                          f"{u[i]['currency']}"
                          f" до {u[i]['salary_to']} {u[i]['currency']}.\n"
                          f"В городе {u[i]['city'] if not None else 'город не указан'}. \n"
                          f"Требования/описание вакансии: {u[i]['requirement']} \n"
                          f"Вакансия находится по ссылке: {u[i]['url']} \n")
                break
        print('Спасибо, что воспользовались нашим поиском. \nВозвращайтесь в любое время.')
        break

if __name__ == '__main__':
    main()
