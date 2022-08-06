import requests

def get_vacancies_json(params: dict):
    params['limit'] = 500
    response = requests.get("http://devseye.ru/api/vacancy", params=params)
    return response.json()

def get_vacancy_message_text(params: dict) -> str:
    response = get_vacancies_json(params)
    print(f"Launching get_vacancy_message_text with params {params}")
    vacancies = response['results']
    return_lst = [f"""
Роль: {vacancy['role']}
Локация: {vacancy['location']}
З/П: {vacancy['min_salary']} - {vacancy['max_salary']}

{vacancy['desc']}
    """ for vacancy in vacancies]
    print(f"Return list: {return_lst}")
    return return_lst