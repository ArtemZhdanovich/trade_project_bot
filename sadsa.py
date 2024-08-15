from okx import OkxRestClient
from configs.load_settings import LoadUserSettingData

settings = LoadUserSettingData().load_api_setings()


# Создайте экземпляр API-клиента
api = OkxRestClient(settings['api_key'], settings['secret_key'], settings['passphrase'])

# Задайте параметры
symbol = 'BTC-USDT-SWAP'  # Пример символа (пары)
after_timestamp = 1678886400000  # Unix-время (миллисекунды) для начала интервала
before_timestamp = ''  # Unix-время (миллисекунды) для конца интервала

# Получите свечи (candlesticks)
candlesticks = api.public.get_candlesticks(
    instId=symbol,
    after=after_timestamp,
    before=before_timestamp,
    bar='1Dutc',  # Интервал свечей (например, дневные свечи)
    limit=100  # Максимальное количество свечей
)


print(candlesticks)
