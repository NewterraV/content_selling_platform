from abc import ABC

import requests

from config import settings


class SMSruBase(ABC):
    pass


class APISMSru(SMSruBase):
    """Класс для работы с API SMSru"""
    def __init__(self):

        self.token = settings.SMSRU_API_KEY

    def get_verify_code(self, phone, ip_address: str) -> [int, bool]:

        if settings.ENV_TYPE in ['local', 'test']:
            return 1111

        response = requests.get(f'https://sms.ru/code/call?'
                                f'phone={phone}&ip={ip_address}&api_id'
                                f'={self.token}')
        if response.status_code == 200:
            verify_code = response.json()['code']
            return int(verify_code)
        return False
