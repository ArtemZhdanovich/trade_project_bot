import os
from dotenv import load_dotenv

class LoadUserSettingData:
    def __init__(self):
        pass


    def load_api_setings(self) -> dict:
        load_dotenv()
        return {
            'flag': str(os.getenv("FLAG")),
            'api_key': str(os.getenv("API_KEY")),
            'passphrase': str(os.getenv("PASSPHRASE")),
            'secret_key': str(os.getenv("SECRET_KEY")),
        }


    def load_cache_settings(self) -> dict:
        load_dotenv()
        return {
            'host': str(os.getenv('REDISHOST')),
            'port': int(os.getenv('REDISPORT')),
            'db': int(os.getenv('REDISDB'))
        }
        

    def load_debug_logging_configs(self):
        load_dotenv()
        value = os.getenv('REQUESTDELAY')
        return {
            'max_retries': int(os.getenv('MAXRETRYREQUESTS')),
            'delay': float(value) if '.' in value else int(value),
            'write_logs': bool(os.getenv('WRITELOGS')),
            'debug': bool(os.getenv('DEBUG'))
        }


    def load_user_settings(self) -> dict:
        load_dotenv()
        return {
            'timeframes': tuple(str(os.getenv("TIMEFRAMES")).split(',')),
            'instIds': tuple(str(os.getenv("INSTIDS")).split(',')),
            'leverage': int(os.getenv('LEVERAGE')),
            'risk': float(os.getenv('RISK')),
            'mgnMode': str(os.getenv('MGNMODE'))
        }


    def load_avsl_configs(self) -> dict:
        load_dotenv()
        return {
            'lenghtsFast': int(os.getenv("AVSLLENGHTSFAST")),
            'lenghtsSlow': int(os.getenv("AVSLLENGHTSSLOW")),
            'lenT': int(os.getenv("AVSLLENT")),
            'standDiv': float(os.getenv("AVSLSTANDDIV")),
            'offset': int(os.getenv("AVSLOFFSET"))
        }


    def load_bollinger_bands_settings(self) -> dict:
        load_dotenv()
        return {
            'lenghts': int(os.getenv("BBLENGHTS")),
            'stdev': float(os.getenv("BBSTDEV")),
            'bb_ddof': int(os.getenv('BBDDOF')),
            'bb_mamode': str(os.getenv('BBMAMODE')),
            'bb_talib': bool(os.getenv('BBTALIB')),
            'bb_offset': int(os.getenv('BBOFFSET'))
        }


    def load_alma_configs(self) -> dict:
        load_dotenv()
        return {
            'lenghtsVSlow': int(os.getenv("ALMALENGHTSVSLOW")),
            'lenghtsSlow': int(os.getenv("ALMALENGHTSSLOW")),
            'lenghtsMiddle': int(os.getenv("ALMALENGHTSSMIDDLE")),
            'lenghtsFast': int(os.getenv("ALMALENGHTSFAST")),
            'lenghtsVFast': int(os.getenv("ALMALENGHTSVFAST")),
            'lenghts': int(os.getenv("ALMALENGHTS"))
        }


    def load_rsi_clouds_configs(self) -> dict:
        load_dotenv()
        return {
            'rsi_period': int(os.getenv('RSICLOUDSRSILENGHTS')),
            'rsi_scalar': int(os.getenv('RSICLOUDSRSISCALAR')),
            'rsi_drift': int(os.getenv('RSICLOUDSRSIDRIFT')),
            'rsi_offset': int(os.getenv('RSICLOUDSRSIOFFSET')),
            'rsi_mamode': str(os.getenv('RSICLOUDSMAMODE')),
            'rsi_talib_config': bool(os.getenv('RSICLOUDSRSITALIBCONFIG')),
            'macd_fast': int(os.getenv('RSICLOUDSMACDFAST')),
            'macd_slow': int(os.getenv('RSICLOUDSMACDSLOW')),
            'macd_signal': int(os.getenv('RSICLOUDSMACDSIGNAL')),
            'macd_offset': int(os.getenv('RSICLOUDSMACDOFFSET')),
            'calc_data': str(os.getenv('RSICLOUDSCALCDATA')),
            'macd_talib_config': bool(os.getenv('RSICLOUDSMACDTALIBCONFIG'))
        }


    def load_stoch_rsi_configs(self) -> dict:
        load_dotenv()
        return {
            'stoch_rsi_timeperiod': int(os.getenv('STOCHRSITIMEPERIOD')),
            'stoch_rsi_fastk_period': int(os.getenv('STOCHRSIFASTKPERIOD')),
            'stoch_rsi_fastd_period': int(os.getenv('STOCHRSIFASTDPERIOD')),
            'stoch_rsi_fastd_matype': int(os.getenv('STOCHRSIFASTDMATYPE'))
        }


    def load_vpci_configs(self) -> dict:
        load_dotenv()
        return {
            'vpci_long': int(os.getenv('VPCILONGPERIOD')),
            'vpci_short': int(os.getenv('VPCISHORTPERIOD'))
        }


    def load_adx_configs(self) -> dict:
        load_dotenv()
        value = int(os.getenv('ADXADXRLENGHTS'))
        return {
            'adx_timeperiod': int(os.getenv('ADXTIMEPERIOD')),
            'adx_lenghts_sig': int(os.getenv('ADXLENGHTSSIG')),
            'adx_adxr_lenghts': None if value==0 else value,
            'adx_scalar': int(os.getenv('ADXSCALAR')),
            'adx_talib': bool(os.getenv('ADXTALIB')),
            'adx_tvmode': bool(os.getenv('ADXTVMODE')),
            'adx_mamode': str(os.getenv('ADXMAMODE')),
            'adx_drift': int(os.getenv('ADXDRIFT')),
            'adx_offset': int(os.getenv('ADXOFFSET')),
            'adx_trigger': int(os.getenv('ADXTRIGGER'))
        }


    def load_kama_configs(self) -> dict:
        load_dotenv()
        return {
            'kama_lengths': int(os.getenv('KAMALENGHTS')),
            'kama_fast':  int(os.getenv('KAMAFAST')),
            'kama_slow': int(os.getenv('KAMASLOW')),
            'kama_drift': int(os.getenv('KAMADRIFT')),
            'kama_offset': int(os.getenv('KAMAOFFSET'))
        }


    def load_mesa_adaptive_ma_configs(self) -> dict:
        load_dotenv()
        return {
            'mesa_fastlimit': float(os.getenv('MESAFASTLIMIT')),
            'mesa_slowlimit': float(os.getenv('MESASLOWLIMIT')),
            'mesa_prenan': int(os.getenv('MESAPRENAN')),
            'mesa_talib': bool(os.getenv('MESATALIB')),
            'mesa_offset': int(os.getenv('MESAOFFSET'))
        }


    def load_zigzag_configs(self) -> dict:
        load_dotenv()
        value = os.getenv('ZIGZAGDEVIATION')
        value = float(value) if '.' in value else int(value)
        return {
            'zigzag_legs': int(os.getenv('ZIGZAGLEGS')),
            'zigzag_deviation': value,
            'zigzag_retrace': bool(os.getenv('ZIGZAGRETRACE')),
            'zigzag_last_extreme': bool(os.getenv('ZIGZAGLASTEXTREME')),
            'zigzag_offset': int(os.getenv('ZIGZAGOFFSET'))
        }


    def load_vwma_adx_configs(self):
        load_dotenv()
        return {
            'vwma_adx_vwma_lenghts': int(os.getenv('VWMAADXVWMALENGHTS')),
            'vwma_adx_adx_period': int(os.getenv('VWMAADXADXPERIOD')),
            'vwma_adx_adx_threshold': int(os.getenv('VWMAADXADXTHRESHOLD')),
            'vwma_adx_adx_smooth': int(os.getenv('VWMAADXADXSMOOTH')),
            'vwma_adx_di_period': int(os.getenv('VWMAADXDIPERIOD'))
        }