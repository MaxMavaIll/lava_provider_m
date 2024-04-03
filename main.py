import time

from function import configuration_settings, check_provider_status, create_message, update_settings
from tg_bot.telegram_bot import send_message


def main():
    log, config, setting, wait = configuration_settings()
    while True:

        data = check_provider_status(log, config, setting)

        if data != {}:
            for moniker in data:
                message = create_message(log, config, data[moniker], moniker)
                send_message(log, config, message)
                time.sleep(1)
        # a = terminal(log, config, 'ls')

        update_settings(setting)
        log.info(f"wait {wait} min")
        time.sleep(wait * 60)

if __name__ == '__main__':
    main()