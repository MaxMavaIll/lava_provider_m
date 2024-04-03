import logging

import requests
from requests.exceptions import RequestException

def send_message(log: logging, config: dict, message: str):

        TOKEN = config['telegram_bot']['TOKEN']

        for chat_id in config['telegram_bot']['admins']:
            log.info(f"Відправляю повідомлення -> {chat_id}")

            
            url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
            # url = url + f'/sendMessage?chat_id={chat_id}&text={message}'
            data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
            
            try:
                response = requests.post(url=url, data=data)
                
                if response.status_code == 200:
                    log.info(f"Повідомлення було відправиленно успішно код {response.status_code}")
                    log.debug(f"Отримано через запит:\n{response.text}")
                    return True
                else:
                    log.error(f"Повідомлення отримало код {response.status_code}")
                    log.error(response.text)
                    log.debug(f"url: {url}")
                    log.debug(f"data: {data}")
            except RequestException as e:
                log.error(f"Сталася помилка при спробі відправити запит: {e}")