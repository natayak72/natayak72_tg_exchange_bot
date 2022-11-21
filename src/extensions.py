import json
import requests 
from . import messages as msg


class CBRApi:
    _api_link = 'https://www.cbr-xml-daily.ru/daily_json.js'
    RUB = 'RUB'


    class APIException(Exception):
        def __init__(self, *args):
            if args:
                self.message = args[0]
            else:
                self.message = None

        def __str__(self):
            if self.message:
                return self.message
            else:
                return 'An error occurred while accessing to API'


    def _get_currencies(self):
        res = json.loads(requests.get(self._api_link).text, encoding='utf-8')['Valute']
        res['RUB'] = {"Name": "Российский рубль",
                    "CharCode": "RUB", 
                    "Value": 1}
        return res


    def _check_api_query_correct(self, query_input):
        query = query_input.split()

        if len(query) > 3:
            raise self.APIException(f'{msg.ERROR_MESSAGE_HEADER} Максимальное число аргументов - 3, а не {len(query)}! \n\n{msg.QUERY_FORMAT}')

        try:
            if len(query) == 1:     # 1. один параметр - строка
                if not isinstance(query[0], str):
                    raise self.APIException(f'{msg.ERROR_MESSAGE_HEADER} Код валюты, в которой будем давать ответ, должен быть строкой, а не \"{query[0]}\"! \n\n{msg.QUERY_FORMAT}')
            elif len(query) == 2:   # 2. 10 usd / usd eur
                # 1. тут проверять можно разве что неотрицательность.
                try:
                    if float(query[0]) < 0:
                        raise self.APIException(f'{msg.ERROR_MESSAGE_HEADER} Нельзя запрашивать отрицательное число валюты: {query[0]}')
                except ValueError:
                    pass    # Если там не число, значит, два индекса валют, проверим позже
            elif len(query) == 3:   # 3. три параметра - число, строка, строка
                if not isinstance(query[1], str):
                    raise self.APIException(f'{msg.ERROR_MESSAGE_HEADER} Код конвертируемой валюты должен быть строкой, а не \"{query[1]}\"! \n\n{msg.QUERY_FORMAT}')
                elif not isinstance(query[2], str):
                    raise self.APIException(f'{msg.ERROR_MESSAGE_HEADER} Код валюты, в которую будем конвертировать, должен быть строкой, а не \"{query[2]}\"! \n\n{msg.QUERY_FORMAT}')
                else:
                    if float(query[0]) < 0:
                        raise self.APIException(f'{msg.ERROR_MESSAGE_HEADER} Нельзя запрашивать отрицательное число валюты: {query[0]}')
        except ValueError:
            raise self.APIException(f'{msg.ERROR_MESSAGE_HEADER} Число валюты, которую будем конвертировать, должно быть числом, а не \"{query[0]}\"! \n\n{msg.QUERY_FORMAT}')


    def _check_currencies_is_correct(self, query_input, currencies):
        query = query_input.split()

        if len(query) == 1: # 1. USD
            query_currency = query[0]
            if query_currency not in currencies.keys():
                raise self.APIException(f'{msg.ERROR_MESSAGE_HEADER} {msg.get_invalid_currency_message(query_currency)}\n\n' \
                    f'{msg.get_values_message(self.get_currencies_list(currencies))}')
        elif len(query) == 2:   # 1. 10 USD или USD EUR
            try:  # 10 USD
                query_count = float(query[0])
                query_currency = query[1]
                if query_currency not in currencies.keys():
                    raise self.APIException(f'{msg.ERROR_MESSAGE_HEADER} {msg.get_invalid_currency_message(query_currency)}\n\n' \
                        f'{msg.get_values_message(self.get_currencies_list(currencies))}')
            except ValueError:    # USD EUR 

                query_currency = query[0]    # USD
                target_currency = query[1]   # EUR

                if query_currency not in currencies.keys():
                    raise self.APIException(f'{msg.ERROR_MESSAGE_HEADER} {msg.get_invalid_currency_message(query_currency)}\n\n' \
                        f'{msg.get_values_message(self.get_currencies_list(currencies))}')
                
                if target_currency not in currencies.keys():
                    raise self.APIException(f'{msg.ERROR_MESSAGE_HEADER} {msg.get_invalid_currency_message(target_currency)}\n\n' \
                        f'{msg.get_values_message(self.get_currencies_list(currencies))}')
        else:   # USD RUB 100
            query_currency = query[1]    # USD
            target_currency = query[2]   # RUB

            if query_currency not in currencies.keys():
                raise self.APIException(f'{msg.ERROR_MESSAGE_HEADER} {msg.get_invalid_currency_message(query_currency)}\n\n' \
                    f'{msg.get_values_message(self.get_currencies_list(currencies))}')
            
            if target_currency not in currencies.keys():
                raise self.APIException(f'{msg.ERROR_MESSAGE_HEADER} {msg.get_invalid_currency_message(target_currency)}\n\n' \
                    f'{msg.get_values_message(self.get_currencies_list(currencies))}')



    def get_currencies_list(self, currencies_dict=None):
        if not currencies_dict:
            return [(value["CharCode"], value["Name"]) for value in self._get_currencies().values()]
        else:
            return [(value["CharCode"], value["Name"]) for value in currencies_dict.values()]


    def _calculate_price(self, query_input, currencies) -> float:
        query = query_input.split()

        if len(query) == 1: # USD
            query_currency = query[0]
            query_result = currencies[query_currency]["Value"]
            
        elif len(query) == 2:   # 10 USD или USD EUR
            try:    # 10 USD
                query_count = float(query[0])
                query_currency = query[1]
                query_result = currencies[query_currency]['Value'] * query_count
            except ValueError:   # USD EUR
                query_currency = query[0]   
                target_currency = query[1]
                target_currency_in_rub = currencies[target_currency]['Value']
                query_currency_in_rub = currencies[query_currency]['Value']
                query_result = query_currency_in_rub / target_currency_in_rub
                
        else:   # 10 USD EUR
            query_count = float(query[0])
            query_currency = query[1]
            target_currency = query[2]

            if target_currency == self.RUB:
                    query_result = currencies[query_currency]['Value'] * query_count
            else:
                target_currency_in_rub = currencies[target_currency]['Value']
                query_currency_in_rub = currencies[query_currency]['Value']
                query_result = query_currency_in_rub * query_count / target_currency_in_rub
            

        return float(f'{query_result : .2f}')


    def get_price(self, query: str) -> float:
        """
        Обрабатывает запросы вида "Десять долларов США в рублях: 10 USD RUB"

        """
        # 1. _check_api_query_correct
        try:
            self._check_api_query_correct(query)
        except self.APIException as error:
            return str(error)

        currencies = self._get_currencies()

        # 2. _check_currencies_is_correct
        try:
            self._check_currencies_is_correct(query, currencies)
        except self.APIException as error:
            return str(error)

        # 3. возврат результата
        return self._calculate_price(query, currencies)