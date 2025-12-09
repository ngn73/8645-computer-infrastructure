import logging as logger
import re
from app_settings import app_config

class app_logger:
    
    def __init__(self, loggername:str):
        myConfig = app_config()
        #Get Logging Settings
        logging_config = myConfig.getLoggingSettings()
        logging_active = logging_config['active']
        logging_filename = logging_config['filename']
        logging_level = logging_config['level']
        logging_format = logging_config['format']
        logging_silence_list = logging_config['silence_list']
        if(logging_level == 'DEBUG'):
            log_level=logger.DEBUG
        elif(logging_level == 'INFO'):
            log_level=logger.INFO
        elif(logging_level == 'WARNING'):
            log_level=logger.WARNING
        elif(logging_level == 'ERROR'):
            log_level=logger.ERROR
        elif(logging_level == 'CRITICAL'):
            log_level=logger.CRITICAL
        else:
            log_level = 0 #deferring to the root logger's level.

        self.logger = None
        if(logging_active == '1'):  #Return None if not active
            #configure logger
            logger.basicConfig(format=logging_format, filename=logging_filename, encoding='utf-8', level=log_level)

            self.logger = logger.getLogger(__name__)

            #suppress logging from other module
            silenced_modules = [x.strip() for x in re.split(r",\s*", logging_silence_list)]
            for silenced_module in silenced_modules:
                logger.getLogger(silenced_module).setLevel(logger.WARNING)
            
        else:
            logger.disable()
        

    # record a log
    def logInfoMessage(self, str_message:str):
        self.logger.info(str_message)
        
    # record a log
    def logDebugMessage(self, str_message:str):
        self.logger.debug(str_message)

    # record a log
    def logWarningMessage(self, str_message:str):
        self.logger.warning(str_message)
        
    # record a log
    def logErrorMessage(self, str_message:str):
        self.logger.error(str_message)