import logging
import toml
import pexpect
import json

from logging.handlers import TimedRotatingFileHandler

config_toml = toml.load("config.toml")

level_logging_cli = logging.INFO
level_logging_f = logging.DEBUG


def configuration_settings():
    
    log = logging.getLogger(__name__)
    log.setLevel(level_logging_cli)

    log_s = logging.StreamHandler()
    log_s.setLevel(level_logging_cli)
    formatter2 = logging.Formatter(
        "%(name)s %(asctime)s %(levelname)s %(message)s")
    log_s.setFormatter(formatter2)

    log_f = TimedRotatingFileHandler(
        f"logs/main.log",
        when=config_toml['logging']['time'],
        interval=config_toml['logging']['interval'],
        backupCount=config_toml['logging']['backup_count'])
    log_f.setLevel(level_logging_f)
    formatter2 = logging.Formatter(
        "%(name)s %(asctime)s %(levelname)s %(message)s")
    log_f.setFormatter(formatter2)

    log.addHandler(log_s)
    log.addHandler(log_f)

    with open('settings.json', 'r') as file:
        settings = json.load(file)



    return log, config_toml, settings, config_toml['time_wait']

def update_settings(setting_json: dict = {}) -> None:
    with open('settings.json', 'w') as file:
        json.dump(setting_json, file)

# def check_provider_status(
#           log: logging, 
#           config: dict,
#           setting: dict
#           ):
    
#     bot_dict = dict()

#     for account in config['accounts']:
#         log.info(f"Moniker: {account} | {config['accounts'][account]}")
#         command = f'lavap q pairing account-info {config["accounts"][account]} -o json --node https://lava-testnet-rpc.polkachu.com:443'

#         data = terminal(log, config, command)
#         keys = ['provider', 'frozen', 'unstaked']

#         for status in data:
#             if status in keys:
#                 for provider in data[status]:
#                     moniker = provider['moniker']
#                     chain = provider['chain']
                    
#                     if moniker not in setting:
#                         setting[moniker] = {}
                    
#                     if moniker not in bot_dict:
#                         bot_dict[moniker] = {}
                    
                    
#                     if status == 'provider':
#                         stat = 'Active'
#                         if chain not in setting[moniker]:
#                             setting[moniker][chain] = stat
                        
#                         log.info(f"{chain}: {stat}")
#                         if setting[moniker][chain] != stat:
#                             bot_dict[moniker][chain] = stat
#                             setting[moniker][chain] = stat

                            
                    
#                     elif status == 'frozen':
#                         stat = 'Frozen'
#                         if chain not in setting[moniker]:
#                             setting[moniker][chain] = stat
                        
#                         log.info(f"{chain}: {stat}")
#                         if setting[moniker][chain] != stat:
#                             bot_dict[moniker][chain] = stat
#                             setting[moniker][chain] = stat


#                     elif status == 'unstaked':
#                         stat = 'Unstaked'
#                         if chain not in setting[moniker]:
#                             setting[moniker][chain] = stat
                        
#                         log.info(f"{chain}: {stat}")
#                         if setting[moniker][chain] != stat:
#                             bot_dict[moniker][chain] = stat
#                             setting[moniker][chain] = stat

                    
#                     if bot_dict[moniker] == {}:
#                         del bot_dict[moniker]
    
#     # bot_dict = setting
#     return bot_dict
                    # if status == 'pr'


def check_provider_status(log: logging, config: dict, setting: dict):
    bot_dict = {}

    status_to_stat = {'provider': 'Active', 'frozen': 'Frozen', 'unstaked': 'Unstaked'}
    keys = status_to_stat.keys()

    for account, account_value in config['accounts'].items():
        log.info(f"Moniker: {account} | {account_value}")
        command = f'lavap q pairing account-info {account_value} -o json --node https://lava-testnet-rpc.w3coins.io:443'
        
        data = terminal(log, config, command)

        for status, stat in status_to_stat.items():
            if status in data:
                for provider in data[status]:
                    update_status_for_provider(log, setting, bot_dict, provider, status, stat)

    return bot_dict

def update_status_for_provider(log, setting, bot_dict, provider, status, stat):
    moniker = provider['moniker']
    chain = provider['chain']

    # Ініціалізуємо словники для moniker, якщо вони ще не існують
    setting.setdefault(moniker, {})
    bot_dict.setdefault(moniker, {})

    # Записуємо статус, якщо він новий або змінився
    current_stat = setting[moniker].get(chain)
    if current_stat != stat:
        log.info(f"{chain}: {stat}")
        bot_dict[moniker][chain] = stat
        setting[moniker][chain] = stat

    # Видаляємо moniker з bot_dict, якщо він не містить жодних змін
    if not bot_dict[moniker]:
        log.info(f"{chain} | No changes found...")
        del bot_dict[moniker]


def create_message(
        log: logging, 
        config: dict,
        data: dict,
        moniker: str
    ):

    message = f'<b>{moniker}</b>\n'
    for chain in data:
        message += f'    {chain}: {data[chain]}\n'

    return message



def terminal(
          log: logging, 
          config: dict,
          command: str
            ) -> str:
        
        cmd = pexpect.spawn(command,timeout=60)
        
        try:
            cmd.expect(pexpect.EOF)
            message = cmd.before.decode()
            json_start_index = message.find('{')
            message = message[json_start_index:]
            message = json.loads(message)
        except pexpect.TIMEOUT:
            message = {}
            log.warn("Час очікування вийшов, шаблон не знайдено.")

        except pexpect.EOF:
            message = {}
            log.warn("Процес завершив роботу до того, як було знайдено шаблон.")

        except Exception as e:
            message = {}
            log.error(f"Сталася непередбачувана помилка: {e}")

        finally:
            cmd.close() 

        return message