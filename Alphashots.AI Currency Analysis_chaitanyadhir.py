'''
we will import the neccessary libraries
'''
import yfinance as yf
import pandas as pd
'''
now we will create logic of decision making
'''

def make_trading_decision(last_price, ma_20, bb_upper, bb_lower, cci):
    """
    We will use the indicators firstly for showing decision based on individual indicators 
    and then overall decision.
    """
    
    # Initialize variable
    decision = "NEUTRAL"
    
    # Initialize dictionary to hold individual signals
    signals = {
        "MA": "",
        "Bollinger Bands": "",
        "CCI": ""
    }
    
    # Analyze Moving Average
    if last_price > ma_20:
        signals["MA"] = "Bullish (buy signal)"
    else:
        signals["MA"] = "Bearish (sell signal)"
    
    # Analyze Bollinger Bands
    if last_price > bb_upper:
        signals["Bollinger Bands"] = "Overbought (sell signal)"
    elif last_price < bb_lower:
        signals["Bollinger Bands"] = "Oversold (buy signal)"
    else:
        signals["Bollinger Bands"] = "Neutral"
    
    # Analyze CCI
    if cci > 100:
        signals["CCI"] = "Overbought (sell signal)"
    elif cci < -100:
        signals["CCI"] = "Oversold (buy signal)"
    else:
        signals["CCI"] = "Neutral"
    
    # Overall logic
    if signals["MA"] == "Bullish (buy signal)" and signals["Bollinger Bands"] == "Oversold (buy signal)" and signals["CCI"] == "Oversold (buy signal)":
        decision = "BUY"
    elif signals["MA"] == "Bearish (sell signal)" and signals["Bollinger Bands"] == "Overbought (sell signal)" and signals["CCI"] == "Overbought (sell signal)":
        decision = "SELL"
    
    return decision, signals


data = yf.download('EURINR=X', start='2023-01-01', end='2024-09-30')


# Calculating Typical Price 
data[('Typical Price', '')] = (data[('High', 'EURINR=X')] + 
                               data[('Low', 'EURINR=X')] + 
                               data[('Close', 'EURINR=X')]) / 3

# Moving Average for Close prices over a 20 day window
data[('MA_20', '')] = data[('Close', 'EURINR=X')].rolling(window=20).mean()

# Bollinger bands
std_dev = data[('Close', 'EURINR=X')].rolling(window=20).std()
data[('BB_Upper', '')] = data[('MA_20', '')] + (2 * std_dev)
data[('BB_Lower', '')] = data[('MA_20', '')] - (2 * std_dev)

# MA of typical price
data[('MA_Typical', '')] = data[('Typical Price', '')].rolling(window=20).mean()

# Define mean absolute deviation function
def mean_absolute_deviation(series):
    return (series - series.mean()).abs().mean()

# Mean deviation for typical price
data[('Mean Deviation', '')] = data[('Typical Price', '')].rolling(window=20).apply(mean_absolute_deviation, raw=False)

# Calcualting commodity channel index (CCI)
data[('CCI', '')] = (data[('Typical Price', '')] - data[('MA_Typical', '')]) / (0.015 * data[('Mean Deviation', '')])

# Verifying the columns created
print(data[[('Close', 'EURINR=X'), ('MA_20', ''), ('BB_Upper', ''), ('BB_Lower', ''), ('CCI', '')]].tail())



# Converting index to datetime with timezone
data.index = pd.to_datetime(data.index)

# Ensuring timezone
data.index = data.index.tz_convert('UTC')

# Chossing the dates
last_day = pd.to_datetime('2024-09-20').tz_localize('UTC')
one_week_later = pd.to_datetime('2024-09-27').tz_localize('UTC')

# Attempt to retrieve data for the specified dates
try:
    last_day_data = data.loc[pd.IndexSlice[last_day, :]]
    one_week_later_data = data.loc[pd.IndexSlice[one_week_later, :]]
    
    print("Data for September 20, 2024:")
    print(last_day_data[['MA_20', 'BB_Upper', 'BB_Lower', 'CCI']])
    
    print("\nData for September 27, 2024:")
    print(one_week_later_data[['MA_20', 'BB_Upper', 'BB_Lower', 'CCI']])
    
except KeyError as e:
    print(f"KeyError: {e}. Check if the dates exist in your DataFrame index.")
except Exception as e:
    print(f"An error occurred: {e}")

date = '2024-09-27'

# Retrieve individual metrics for the specified date
last_price = data.loc[date, ('Close', 'EURINR=X')]
ma_20 = data.loc[date, ('MA_20', '')]
bb_upper = data.loc[date, ('BB_Upper', '')]
bb_lower = data.loc[date, ('BB_Lower', '')]
cci = data.loc[date, ('CCI', '')]

# Get trading decision and signals
trading_decision, signals = make_trading_decision(last_price, ma_20, bb_upper, bb_lower, cci)

# Final decision

print("Signals:")
for indicator, signal in signals.items():
    print(f"{indicator} Signal: {signal}")
print(f"Trading Decision: {trading_decision}")







