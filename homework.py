import logging
import os
import requests
import sys
import telegram
import time

from dotenv import load_dotenv

from exception import (
    ApiError,
    MessageError,
    ParseStatusError,
    ResponseError,
)


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    """Function of checking environments variables."""
    env_variables = (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    for token in env_variables:
        if token is None:
            logger.critical(
                'Error of environments variables.'
                f'"{token}"'
            )
    return all(env_variables)


def send_message(bot, message):
    """Function of sending messages."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as error:
        raise MessageError(f'Error of sending messages {error}.')
    else:
        logger.info('Message sent successfully.')


def get_api_answer(timestamp):
    """Function make request to API."""
    timestamp = timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params=params,
    )
    if response.status_code != 200:
        raise ApiError(f'Not correct status code {response.status_code}.')
    return response.json()


def check_response(response):
    """Function of checking response."""
    if not response:
        raise ResponseError('Not correct response.')

    if 'homeworks' not in response:
        raise TypeError('Homeworks not in response.')

    homeworks = response.get('homeworks')

    if not isinstance(homeworks, list):
        raise TypeError('Another type of homeworks.')

    return response['homeworks']


def parse_status(homework):
    """Function of extracting of results homework."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_VERDICTS.get(homework_status)

    if homework_name is None:
        raise KeyError('Homework without name.')

    if 'status' not in homework:
        raise ParseStatusError('Homework without status.')

    if homework_status not in HOMEWORK_VERDICTS:
        raise KeyError('Homework without verdict.')

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """General logic in work of Bot."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    response = get_api_answer(timestamp)
    homeworks = check_response(response)
    if not check_tokens():
        sys.exit()

    while True:
        try:
            count_homeworks = len(homeworks)
            if response is None:
                logger.error('API dont send response.')
                send_message(
                    bot,
                    'Function get_api_answer having problem.'
                )

            if count_homeworks > 1:
                homework_status = parse_status(homeworks[0])
            else:
                homework_status = parse_status(homeworks)

            if homework_status:
                send_message(bot, homework_status)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            send_message(bot, message)
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
