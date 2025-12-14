import configparser
class app_config:
    def __init__(self):
        try:
            self.config_file = './app_settings.ini'     #Hardcoded ... should not change!
            # Create a ConfigParser object
            self.config = configparser.ConfigParser()
            # Read the configuration file
            self.config.read(self.config_file)
        except FileNotFoundError as e:
            print(f"Error: Cannot find config file {self.config_file} :{e}")
        except configparser.ParsingError as e:
            print(f"Config file {self.config_file} is badly formatted: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during loading config file {self.config_file}:", e)

    def getLoggingSettings(self):
        # Logging values from the configuration file
        try:
            #logging_active_ini = self.config.getboolean('Logging', 'log_active')
            logging_active = self.config.get('Logging', 'log_active')
            logging_path = self.config.get('Logging', 'log_path') 
            logging_level = self.config.get('Logging', 'log_level')
            logging_format = self.config.get('Logging', 'log_format')
            logging_silence_list = self.config.get('Logging', 'log_silence_list')
            logging_settings = {
                'active': logging_active,
                'path': logging_path,
                'level': logging_level,
                'format': logging_format,
                'silence_list': logging_silence_list
                }
            return logging_settings
        except configparser.NoSectionError as e:
            print(f"Missing section in config: {e}")
        except configparser.NoOptionError as e:
            print(f"Missing option in config: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during loading config Folder section in file: {self.config_file}: {e}")

    def getFolderSettings(self):
        # Folder path values from the configuration file
        try:
            csv_dir = self.config.get('Folders', 'csv_dir')
            plot_dir = self.config.get('Folders', 'plot_dir')
            dest_dir = self.config.get('Folders', 'dest_dir')
            staging_dir = self.config.get('Folders', 'staging_dir')
            archive_dir = self.config.get('Folders', 'archive_dir')
            filename_format = self.config.get('Folders', 'filename_format')

            folder_settings = {
                'csv_dir' : csv_dir,
                'plot_dir' : plot_dir,
                'dest_dir' : dest_dir,
                'staging_dir' : staging_dir,
                'archive_dir' : archive_dir,
                'filename_format' : filename_format
                }
            return folder_settings
        except configparser.NoSectionError as e:
            print(f"Missing section in config: {e}")
        except configparser.NoOptionError as e:
            print(f"Missing option in config: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during loading config Logging section in file: {self.config_file}: {e}")

    def getStocksSettings(self):
        # Stock Ticker values from the configuration file
        try:
            stock_tickers = self.config.get('Stocks', 'tickers')
            stock_period = self.config.get('Stocks', 'period')
            stock_interval = self.config.get('Stocks', 'interval')
            stock_settings = {
                'tickers' : stock_tickers,
                'period' : stock_period,
                'interval' : stock_interval
                }
            return stock_settings
        except configparser.NoSectionError as e:
            print(f"Missing section in config: {e}")
        except configparser.NoOptionError as e:
            print(f"Missing option in config: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during loading config Logging section in file: {self.config_file}: {e}")


    def getAllSettings(self):
        # Return a distionary of dictionaries (with the retrieved values)
        logging_settings = self.getLoggingSettings()
        folder_settings = self.getFolderSettings()
        stock_settings = self.getStocksSettings()
        config_settings = {'logging':logging_settings, 'folder':folder_settings, 'stock':stock_settings}
        return config_settings

