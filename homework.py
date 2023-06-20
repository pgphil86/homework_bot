import logging
import os
import requests
import sys
import telegram
import time

from dotenv import load_dotenv

from exception import (
    ApiError,
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
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG
)


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
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logger.error(f'Message not sent, {error}.')
    else:
        logger.debug(f'Bot sent, {message}.')


def get_api_answer(timestamp):
    """Function make request to API."""
    timestamp = timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params,
        )
    except Exception as error:
        raise ApiError(f'Error {error}')
    if response.status_code != 200:
        raise ApiError(f'Not correct status code {response.status_code}.')

    return response.json()


def check_response(response):
    """Function of checking response."""
    if not isinstance(response, dict):
        raise TypeError('Not correct type of response.')
    elif not response:
        raise ResponseError('Not correct response.')
    elif 'homeworks' not in response:
        raise TypeError('Homeworks not in response.')
    elif not isinstance(response['homeworks'], list):
        raise TypeError('Another type of homeworks.')

    return response.get('homeworks')


def parse_status(homework):
    """Extracting function of results homework."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_name is None:
        raise KeyError('Homework without name.')

    if homework_status in HOMEWORK_VERDICTS:
        verdict = HOMEWORK_VERDICTS[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
        # return f'Status of work, "{homework_name}", changed. {verdict}.'
    raise ParseStatusError(f'Unknown status - {homework_status}.')


def main():
    """General logic in work of Bot."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    if not check_tokens():
        sys.exit()

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            count_homeworks = len(homeworks)

            if count_homeworks > 0:
                homework_status = parse_status(homeworks[0])
                send_message(bot, f'{homework_status}')
            else:
                logger.debug('New status not exist.')

        except Exception as error:
            message = f'Error in app: {error}'
            logging.error(message)
            send_message(bot, message)
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
