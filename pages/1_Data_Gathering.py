# STREAMLIT
import streamlit as st
from streamlit_extras.grid import grid
from streamlit_extras.app_logo import add_logo


from datetime import datetime, timezone
import numpy as np
import pandas as pd
import requests
import math
import time
import csv

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio


# --- PAGE CONFIG (BROWSER TAB) ---
st.set_page_config(page_title="Sharktank", page_icon=":shark:", layout="centered", initial_sidebar_state="expanded")


# ---- LOAD ASSETS ----
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style/style.css")

# ---- CACHE SETTING ----
if 'refreshed' not in st.session_state:
    st.session_state.refreshed = True
    st.session_state.dataframe =  pd.DataFrame()
    st.session_state.rawdata =  {}
    st.session_state.lastpair =  ""



def Clock(delay):
    _delay=delay
    time_now = datetime.now(timezone.utc)
    day_start = time_now.strftime("%Y-%m-%dhh:mm:ss")
    day_start = time_now.strptime(day_start, "%Y-%m-%dhh:mm:ss")
    day_start = int(datetime.timestamp(day_start))
    time_now = int(datetime.timestamp(time_now))
    session = time_now-(_delay*60)
    return [day_start,time_now,session]


def agg_ohlcv(_symbols, _timeframe, _start, _end):
    dfs = []  # list to hold dataframes
    for _symbol in _symbols:
        params = {
            'symbols': _symbol,
            'interval': _timeframe,
            'from' : _start,
            'to' : _end
        }
        response = requests.get('https://api.coinalyze.net/v1/ohlcv-history', headers=coinalize_headers, params=params)
        response_json = response.json()

        for item in response_json:
            temp_data = item['history']
            df = pd.DataFrame(temp_data)
            new_columns = {'t': 'TimeStamp',
                           'o': 'Open',
                           'h': 'High',
                           'l': 'Low',
                           'c': 'Close',
                           'v': 'Volume',
                           'bv': 'BuyVolume',
                           'tx': 'Trades',
                           'btx': 'BuyTrades'}
            df = df.rename(columns=new_columns)
            dfs.append(df)

    combined_df = pd.concat(dfs, axis=0)  # concatenate dataframes

    # Group by timestamp and aggregate
    aggregated_df = combined_df.groupby('TimeStamp').agg({
        'Open': 'mean',
        'High': 'max',
        'Low': 'min',
        'Close': 'mean',
        'Volume': 'sum',
        'BuyVolume': 'sum',
        'Trades': 'sum',
        'BuyTrades': 'sum'
    }).reset_index()

    return aggregated_df



def agg_longshort(_symbols, _timeframe, _start, _end):
    dfs = []  # list to hold dataframes
    for _symbol in _symbols:
        params = {
            'symbols': _symbol,
            'interval': _timeframe,
            'from' : _start,
            'to' : _end
        }
        response = requests.get('https://api.coinalyze.net/v1/long-short-ratio-history', headers=coinalize_headers, params=params)
        response_json = response.json()

        for item in response_json:
            temp_data = item['history']
            df = pd.DataFrame(temp_data)
            new_columns = {'t': 'TimeStamp',
                           'r': 'LSRatio',
                           'l': 'LongRatio',
                           's': 'ShortRatio'}
            df = df.rename(columns=new_columns)
            dfs.append(df)

    combined_df = pd.concat(dfs, axis=0)  # concatenate dataframes

    # Group by timestamp and aggregate
    aggregated_df = combined_df.groupby('TimeStamp').agg({
        'LSRatio': 'mean',
        'LongRatio': 'mean',
        'ShortRatio': 'mean',
    }).reset_index()

    return aggregated_df



def agg_openinterest(_symbols, _timeframe, _start, _end, _convert):
    dfs = []  # list to hold dataframes
    for _symbol in _symbols:
        params = {
            'symbols': _symbol,
            'interval': _timeframe,
            'from' : _start,
            'to' : _end,
            'convert_to_usd': _convert
        }
        response = requests.get('https://api.coinalyze.net/v1/open-interest-history', headers=coinalize_headers, params=params)
        response_json = response.json()

        for item in response_json:
            temp_data = item['history']
            df = pd.DataFrame(temp_data)
            new_columns = {'t': 'TimeStamp',
                           'o': 'OIOpen',
                           'h': 'OIHigh',
                           'l': 'OILow',
                           'c': 'OIClose'}
            df = df.rename(columns=new_columns)
            dfs.append(df)

    combined_df = pd.concat(dfs, axis=0)  # concatenate dataframes

    # Group by timestamp and aggregate
    aggregated_df = combined_df.groupby('TimeStamp').agg({
        'OIOpen': 'mean',
        'OIHigh': 'max',
        'OILow': 'min',
        'OIClose': 'mean',
    }).reset_index()

    return aggregated_df




def agg_liquidations(_symbols, _timeframe, _start, _end):
    dfs = []  # list to hold dataframes
    for _symbol in _symbols:
        params = {
            'symbols': _symbol,
            'interval': _timeframe,
            'from' : _start,
            'to' : _end
        }
        response = requests.get('https://api.coinalyze.net/v1/liquidation-history', headers=coinalize_headers, params=params)
        response_json = response.json()

        for item in response_json:
            temp_data = item['history']
            df = pd.DataFrame(temp_data)
            new_columns = {'t': 'TimeStamp',
                           'l': 'LongLiquidation',
                           's': 'ShortLiquidation'}
            df = df.rename(columns=new_columns)
            dfs.append(df)

    combined_df = pd.concat(dfs, axis=0)  # concatenate dataframes

    # Group by timestamp and aggregate
    aggregated_df = combined_df.groupby('TimeStamp').agg({
        'LongLiquidation': 'sum',
        'ShortLiquidation': 'sum',
    }).reset_index()

    return aggregated_df


def agg_fundingrates(_symbols, _timeframe, _start, _end):
    dfs = []  # list to hold dataframes
    for _symbol in _symbols:
        params = {
            'symbols': _symbol,
            'interval': _timeframe,
            'from' : _start,
            'to' : _end
        }
        response = requests.get('https://api.coinalyze.net/v1/funding-rate-history', headers=coinalize_headers, params=params)
        response_json = response.json()

        for item in response_json:
            temp_data = item['history']
            df = pd.DataFrame(temp_data)
            new_columns = {'t': 'TimeStamp',
                           'o': 'FROpen',
                           'h': 'FRHigh',
                           'l': 'FRLow',
                           'c': 'FRClose'}
            df = df.rename(columns=new_columns)
            dfs.append(df)

    combined_df = pd.concat(dfs, axis=0)  # concatenate dataframes

    # Group by timestamp and aggregate
    aggregated_df = combined_df.groupby('TimeStamp').agg({
        'FROpen': 'mean',
        'FRHigh': 'max',
        'FRLow': 'min',
        'FRClose': 'mean',
    }).reset_index()

    return aggregated_df

def agg_markets(base, qoute):
    available_markets = []
    pairs = requests.get('https://api.coinalyze.net/v1/future-markets', headers=coinalize_headers)
    pairs = pairs.json()
    for pair in pairs:
        if pair['base_asset']==base and pair['quote_asset']==qoute:
            if pair['expire_at']==None and pair['has_long_short_ratio_data']==True and pair['has_ohlcv_data']==True and pair['has_buy_sell_data']==True:
              available_markets.append(pair['symbol'])
    return available_markets

def basic_markets(base, qoute):
    available_markets = []
    pairs = requests.get('https://api.coinalyze.net/v1/future-markets', headers=coinalize_headers)
    pairs = pairs.json()
    for pair in pairs:
        if pair['base_asset']==base and pair['quote_asset']==qoute:
            if pair['expire_at']==None and pair['has_ohlcv_data']==True:
              available_markets.append(pair['symbol'])
    return available_markets



# --- MAIN PAGE ---
with st.container():
    st.title("Data Gathering")
    
    # DATA COLLECTION, 
    with st.form("Collect"):
        _api_key = st.text_input( "Enter your **Coinalyze** API Key")
        col = grid([1, 1], vertical_align="center")
        _base_coin = col.text_input( "Enter your **Base** asset symbol in UPPERCASE", "BTC")
        _qoute_coin = col.text_input( "Enter your **Qoute** asset symbol in UPPERCASE", "USD")
        
        if st.form_submit_button("Collect", use_container_width=True):
            with st.spinner("Connecting..."):
                coinalize_headers = {'api_key': f'{_api_key}'}
                t=1440*30*96
                end= Clock(t)[1]
                start= Clock(t)[2]

                base_coin = f'{_base_coin}'
                qoute_coin = f'{_qoute_coin}'
                full_asset = agg_markets(base_coin, qoute_coin)
                basic_asset = basic_markets(base_coin, qoute_coin)
                st.success(f"Connected to {_api_key}.")
                st.session_state.lastpair = full_asset

            st.write(f"""All available markets for {base_coin} / {qoute_coin}: \n 
                         {basic_asset}""")
            st.write(f"""Available aggregated markets for {base_coin} / {qoute_coin}: \n 
                         {full_asset}""")
            timeframe = '30min'
            # Options: "1min" "5min" "15min" "30min" "1hour" "2hour" "4hour" "6hour" "12hour" "daily"
            buffer = st.progress(0.0, text="Data Collecting in process...")
            
            ohlcv_df = agg_ohlcv(basic_asset, timeframe, start, end)
            st.toast("OHLCV extracted: " + f"`{len(ohlcv_df)}`")
            buffer.progress((1/5), text=f"Data Collecting in process...")
            
            oi_df = agg_openinterest(full_asset, timeframe, start, end, "true")
            st.toast("Open Interest extracted: " + f"`{len(oi_df)}`")
            buffer.progress((2/5), text=f"Data Collecting in process...")
            
            liq_df = agg_liquidations(full_asset, timeframe, start, end)
            st.toast("Liquidations extracted: " + f"`{len(liq_df)}`")
            buffer.progress((3/5), text=f"Data Collecting in process...")
            
            lsr_df = agg_longshort(full_asset, timeframe, start, end)
            st.toast("Long/Short ratio extracted: " + f"`{len(lsr_df)}`")
            buffer.progress((4/5), text=f"Data Collecting in process...")
            
            fr_df = agg_fundingrates(full_asset, timeframe, start, end)
            st.toast("Funding Rate extracted: " + f"`{len(fr_df)}`")
            buffer.progress((5/5), text=f"Data Collecting in process...")
            
            st.info("Data Collection is done!")
            
            df = pd.DataFrame()

            df['TimeStamp']=            ohlcv_df['TimeStamp'].copy()
            df['DateTime'] =            [datetime.fromtimestamp(i).strftime('%Y-%m-%d %H:%M:%S.%d')[:-3] for i in df['TimeStamp']]
            df['Open']=                 ohlcv_df['Open'].copy()
            df['High']=                 ohlcv_df['High'].copy()
            df['Low']=                  ohlcv_df['Low'].copy()
            df['Close']=                ohlcv_df['Close'].copy()
            df['Side'] =                df.apply(lambda row: 'Buy' if row['Close'] > row['Open'] else 'Sell', axis=1)
            df['Volume']=               ohlcv_df['Volume'].copy()
            df['BuyVol']=               ohlcv_df['BuyVolume'].copy()
            df['SellVol'] =             ohlcv_df['Volume'] - ohlcv_df['BuyVolume']
            df['Delta'] =               df['BuyVol'] - df['SellVol']
            df['Trade'] =               ohlcv_df['Trades']
            df['BuyTrades'] =           ohlcv_df['BuyTrades']
            df['SellTrades'] =          ohlcv_df['Trades'] - ohlcv_df['BuyTrades']
            df['LSRatio']=              lsr_df['LSRatio'].copy()
            df['LongRatio']=            lsr_df['LongRatio'].copy()*0.01
            df['ShortRatio']=           lsr_df['ShortRatio'].copy()*0.01
            df['OIOpen']=               oi_df['OIOpen'].copy()
            df['OIHigh']=               oi_df['OIHigh'].copy()
            df['OILow']=                oi_df['OILow'].copy()
            df['OIClose']=              oi_df['OIClose'].copy()
            df['OIChange'] =            df['OIClose'] - df['OIOpen']
            df['LongLiquidation']=      liq_df['LongLiquidation'].copy()
            df['ShortLiquidation']=     liq_df['ShortLiquidation'].copy()
            df['FROpen']=               fr_df['FROpen'].copy()
            df['FRHigh']=               fr_df['FRHigh'].copy()
            df['FRLow']=                fr_df['FRLow'].copy()
            df['FRClose']=              fr_df['FRClose'].copy()

            st.session_state.dataframe = df
            data = df.to_dict('records')
            data = sorted(data, key=lambda x: x['DateTime'])
            df_sorted = df.sort_values('DateTime')
            data = df_sorted.to_dict('records')
            data = sorted(data, key=lambda x: x['TimeStamp'])
            df_sorted = df.sort_values('TimeStamp')
            data = df_sorted.to_dict('records')
            st.session_state.rawdata = data

            st.dataframe(st.session_state.dataframe)
            
    # SAVE CSV
    if len(st.session_state.rawdata)!=0:
        if st.button("Save as CSV"):
            st.session_state.dataframe.to_csv(f"assets/{st.session_state.lastpair}.csv", index=False)
            
            
    # CANDLESTICK CHART
    if len(st.session_state.rawdata)!=0:
        df = st.session_state.dataframe
        candlestick_trace = go.Candlestick(x=df['DateTime'],open = df['Open'],high=df['High'],low=df['Low'],close=df['Close'])
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.0)
        fig.add_trace(candlestick_trace, row=1, col=1)
        st.plotly_chart(fig, theme="streamlit")