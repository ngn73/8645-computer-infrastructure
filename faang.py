#!/usr/bin/env python3

'''
Author:Niall Naughton
Date:16/11/2025
Description:
Script migrated initially from Jupyter Notebook
* Downloads the Ticker data for 'META', 'AAPL', 'AMZN', 'NFLX', 'GOOG' with yFinance library (or whatever stocks configured)
* Saves the data to a timestamped CSV file with MultiIndex Headers
* Generates a line plot of hourly Close prices over the past 5 days (or whatever time periods configured)
* Saves the plot as a PNG file with a timestamped filename

Dependencies:
Beside standard libraries (listed in requirements.txt), this script also requires the following custom libraries:
* app_settings (defined in app_settings.py) for configuration management
* app_logger (defined in app_logger.py) for logging management

Configuration:
This script is configured with a collection of settings within an ini file (app_setting.ini)
'''

import yfinance as yf
import shutil
from requests.exceptions import HTTPError, ConnectionError, Timeout
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import glob
from datetime import datetime
import os
from pathlib import Path
from app_settings import app_config
import app_logger as logger

#Read all config settings
def init_Logging():
    #Get Logging Settings
    logging_config = myConfig.getLoggingSettings()
    logging_active = logging_config['active']
    logging_filename = logging_config['filename']
    logging_level = logging_config['level']
    logging_format = logging_config['format']
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

    self_logger = None
    if(logging_active == '1'):  #Return None if not active
        #configure logger
        logger.basicConfig(format=logging_format, filename=logging_filename, encoding='utf-8', level=log_level)

        self_logger = logger.getLogger(__name__)
        #suppress logging from yfinance module
        logger.getLogger('yfinance').setLevel(logger.WARNING)
        logger.getLogger('peewee').setLevel(logger.WARNING)
        logger.getLogger('urllib3').setLevel(logger.WARNING)
    return self_logger

#Archive the all CVS files in root 'data' folder and move to 'archive' folder
def archiveData() :
    #Get list of CSV files in source directory
    csv_files = [f for f in os.listdir(dest_dir) if f.lower().endswith('.csv')]

    for file in csv_files:
        source_path = os.path.join(dest_dir, file)
        archive_path = os.path.join(archive_dir, file)

        # Move file
        if os.path.exists(source_path):
            shutil.move(source_path, archive_path)
            my_logger.logDebugMessage(f"Archived: {file} to {archive_path}")
        else:
            my_logger.logDebugMessage(f"File not found: {source_path}") 

# Download last 5 days of hourly data for Meta, Apple, Amazon, Netflix, Google stocks
def extractData(_tickers, _period, _interval, _retries=3) :
    
    for attempt in range(_retries):
        try:
            faang_df = yf.download(_tickers, period=_period, interval=_interval, group_by="ticker", auto_adjust=True)
            print("Downloaded DF shape:", faang_df.shape)
            if faang_df.empty:
                raise ValueError("Downloaded data is empty.")
            if faang_df.isnull().values.any():
                raise ValueError("Downloaded data contains NaN values.")
            my_logger.logDebugMessage("yFinance Data extraction successful.")
            return faang_df
        
        except HTTPError as e:
            my_logger.logErrorMessage(f"HTTP Error (attempt {attempt + 1}/{_retries}): {e}")
            if attempt == _retries - 1:
                raise
                
        except ConnectionError as e:
            my_logger.logErrorMessage(f"Connection Error (attempt {attempt + 1}/{_retries}): {e}")
            if attempt == _retries - 1:
                raise
                
        except Timeout as e:
            my_logger.logErrorMessage(f"Timeout Error (attempt {attempt + 1}/{_retries}): {e}")
            if attempt == _retries - 1:
                raise
                
        except ValueError as e:
            my_logger.logErrorMessage(f"Validation Error: {e}")
            return pd.DataFrame()  # Return empty DataFrame
        
        except Exception as e:
            my_logger.logErrorMessage(f"Unexpected error: {type(e).__name__}: {e}")
            return pd.DataFrame()   # Return empty DataFrame

        return pd.DataFrame()   # Return empty DataFrame

#Read a CSV file and return a Dataframe
def readCSV(file_path:str):
        base_filename = ''
        try:
            cvs_filepath = os.path.join(file_path, "*.csv" )
            matches = glob.glob(cvs_filepath)

            # No CSV files found
            if not matches:
                raise FileNotFoundError(f"No CSV files found in directory: {file_path}")

            # Use the first matched CSV file
            csv_file = matches[0]
            
            # Read the CSV file with 3 Headers
            # Attempt to read CSV
            try:
                df = pd.read_csv(csv_file, header=[0, 1, 2], index_col=0)
                my_logger.logDebugMessage(F"Successfully read the CSV file {csv_file}")
            except Exception as e:
                raise ValueError(f"Failed to read CSV file '{csv_file}': {e}")
                df = None

            base_filename = Path(csv_file).stem
        except Exception as e:
            # Catch-all to report any unexpected issue
            my_logger.logErrorMessage(f"Error in readCSV(): {e}")
            df = None
        
        return df, base_filename  #Return filename of csv file (to be used in image filename)

#Save Dataframe of FAANG data into a CSV file
def saveData(df:pd.DataFrame, csvfilename:str) :    
    try:
        csv_file =  csvfilename
        staging_data_filepath = os.path.join(staging_dir, csv_file )
        dest_data_filepath = os.path.join(dest_dir, csv_file )
        print(f"staging_data_filepath = {staging_data_filepath}")
        df.to_csv(staging_data_filepath)
        

        # Verify file was created
        if os.path.exists(staging_data_filepath):
            my_logger.logDebugMessage(f"yFinance CSV File {csv_file} generated in Staging folder.")
            print(f"{staging_data_filepath} exists and is about to archive")
            #archive previous file/s
            archiveData()
            #Move from staging to destination
            shutil.move(staging_data_filepath, dest_data_filepath)
            my_logger.logDebugMessage(f"yFinance CSV File {csv_file} moved to data folder.")
            return staging_data_filepath
        else:
            my_logger.logDebugMessage("yFinance CSV File not generated in Staging folder.")
            print("file was not created")
            return None
    except Exception as e:
        my_logger.logErrorMessage(f"Unexpected error saving data: {type(e).__name__}: {e}")
        return None

#Plot a lineplot of FAANG data, nd save as a PNG image file
def plot_data(df_stock:pd.DataFrame, filename:str):
  
    png_filename = filename + ".png"
    plot_filepath = os.path.join(plot_dir, png_filename )

    df_stock.index = pd.to_datetime(df_stock.index)
    df_stock.index.name = 'Datetime'

    #print(df_stock.head(10))

    try:
        df_stock = df_stock.sort_index(axis=1)

        plt.figure(figsize=(10,5))
        for stock in ['META', 'AAPL', 'AMZN', 'NFLX', 'GOOG']:
            try:
                plt.plot(
                    df_stock.index,
                    df_stock[(stock, 'Close')],
                    marker='o',
                    label=stock
                )
            except KeyError as e:
                my_logger.logWarningMessage(f"Stock {stock} missing in dataframe: {e}")
            except Exception as e:
                my_logger.logErrorMessage(f"Unexpected error plotting {stock}: {e}")

        plt.title('Stock Hourly Closing Price (Past 5 days)')
        plt.xlabel('Date')
        plt.ylabel('Close Price')
        plt.grid(True)
        plt.legend()

        # Format the x-axis dates
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d-%Y'))
        #plt.xticks(rotation=45)

        plt.tight_layout()

        my_logger.logDebugMessage(f"Plot generated from CSV file.")
    except Exception as e:
        my_logger.logErrorMessage(
            f"Error generating plot: {e}",
            exc_info=True  # <-- this logs full traceback
        )
        plt.close()
        return False
    
# Saving the output file
    try:
        plt.savefig(plot_filepath, dpi=300, bbox_inches='tight')
        my_logger.logInfoMessage(f"Plot saved to file {plot_filepath}")
    except Exception as e:
        my_logger.logErrorMessage(
            f"Error saving plot to {plot_filepath}: {e}",
            exc_info=True
        )
        plt.close()
        return False

    # Show the plot
    try:
        plt.show()
    except Exception as e:
        my_logger.logWarningMessage(f"Error displaying plot: {e}")

    plt.close()
    return True

#Download FAANG data from yFinance and save to a CSV file
def getFAANGData(faang_tickers, faang_period, faang_interval, filename:str) :
    my_logger.logDebugMessage(f"Starting FAANG data retrieval process for {faang_tickers} with interval '{faang_interval}' over period '{faang_period}'.")
    
    df= extractData(faang_tickers, faang_period, faang_interval)
    if (df.empty == False) :
        #Generate a file in Staging folder, and archive old csv
        saveData(df, filename)
    my_logger.logDebugMessage("FAANG data retrieval process completed.")

#initially create folders
Path("logs").mkdir(parents=True, exist_ok=True)
Path("data/archive").mkdir(parents=True, exist_ok=True)
Path("data/plots").mkdir(parents=True, exist_ok=True)
Path("data/staging").mkdir(parents=True, exist_ok=True)

#get base filename for csv, png, and log files
basefilename = datetime.now().strftime("%Y%m%d-%H%M%S")

# Setup Config Settings
myConfig = app_config()

#Setup Logging
my_logger = logger.app_logger(__name__, basefilename)

#Get folders from config
folder_config = myConfig.getFolderSettings()
dest_dir =  folder_config['dest_dir']
staging_dir = folder_config['staging_dir']
archive_dir = folder_config['archive_dir']
plot_dir = folder_config['plot_dir']

#get Stock settings from config
faang_config = myConfig.getStocksSettings()
faang_tickers = faang_config['tickers']
faang_period = faang_config['period']
faang_interval = faang_config['interval']

#Download FAANG data from yFinance and Save to CSV file
csv_filename = basefilename + ".csv"
getFAANGData(faang_tickers, faang_period, faang_interval, csv_filename)
print(f"yFinance data extracted for {faang_tickers} and saved to CSV file :{csv_filename} to folder {dest_dir}")

#Read the CSV file
df_csv, filename = readCSV(dest_dir)
if(df_csv.empty == False):
    print(f"Successfully read csv file {filename + ".csv"}")
    #Plot the data and save as PNG file with same filename as csv
    if(plot_data(df_csv, filename)):
        print(f"Successfully saved plot to png file : {filename + ".png"}")
    else:
        print(f"Failed to save plot to png file : {filename + ".png"} (review log file)")
else:
    print(f"Failed to read csv file (review log file)")
