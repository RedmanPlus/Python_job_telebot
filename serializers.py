import datetime

class Vacancy:
    def __init__(self, vac_dct: dict):
        self.id = vac_dct['id']
        self.role = vac_dct['role']
        self.skill = vac_dct['skill']
        self.technologies = vac_dct['technologies']
        self.datetime = datetime.datetime.fromisoformat(vac_dct['add_date'][:-1])
        self.min_salary = vac_dct['min_salary']
        self.max_salary = vac_dct['max_salary']
        self.salary_currency = vac_dct['salary_currency']
        self.desc = vac_dct['desc']
        self.tasks = vac_dct['tasks']
        self.requirements = vac_dct['requirements']
        self.channel = vac_dct['channel_id']
        self.message_id = vac_dct['message_id']
    
    def __str__(self):
        return self.role 
