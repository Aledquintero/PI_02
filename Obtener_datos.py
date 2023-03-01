import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import re
import ta

# Crea una variable que obtiene la fecha actual
fecha_actual = datetime.today().strftime('%Y-%m-%d')





#================== Funciones ======================

# Crea una funcion para traer los datos desde yahoo finance y exportarlos como csv
def extraer_datos(ticker, inicio, nombre):

  # Extrae los datos de Yahoo Finance
  df = pd.DataFrame(yf.download(ticker, start = inicio, end = fecha_actual))
  df = df.reset_index()

  #================= Indicadores ==================================
 
  #=== RSI ====
  # Calcular el RSI con un período de 14 días
  rsi_period = 14
  df['rsi'] = ta.momentum.RSIIndicator(df['Close'], rsi_period).rsi()
  #=== Ema ====
  # Calcular la EMA con un período de 20 días
  ema_period = 20
  df['ema'] = ta.trend.EMAIndicator(df['Close'], ema_period).ema_indicator()
  #=== Tendencia ====
  df["Tendencia"] = np.where((df.Close > df.ema) & (df.rsi > 50), "Alcista", "Bajista") #si el rsi es mayor a 50 y el precio está por encima de la ema es alcista, de lo contrario bajista
  #=== rsi_estado ===
  condiciones = [
    (df.rsi > 70),
    (df.rsi < 30),
    ((df.rsi >= 30) & (df.rsi <= 70))
  ]

  resultados = ['sobrevalorado', 'infravalorado', 'neutral']

  df['rsi_estado'] = np.select(condiciones, resultados, default='')

  df = df.round(2)
  #================ Exportación ===================================
  df.to_csv(f'csv/{nombre}.csv', index=False)

  return f"Se exportó {ticker}"

# Ejecutamos la función
extraer_datos('^GSPC', '1990-01-01', "S&P500") #S&P500 Index 
extraer_datos('^TNX', '1990-01-01', "US10Y") #Bonos 10Y EEUU
extraer_datos('^IXIC', '1990-01-01', "NASDAQ") # Nasdaq Index




#================== PE-Ratio ======================

# Carga los datos de PE-ratio por mes 
sype = pd.read_html('https://www.multpl.com/s-p-500-pe-ratio/table/by-month', header=0)[0]

# Filtra los datos a partir de los 90's y cambia el nombre de la columna 'Value'
sype = sype.loc[sype.Date >= '1990-01-01'].rename({'Value Value' : 'PE-ratio'}, axis = 1)

# Formatear la columna "fecha" como una cadena
sype['Date'] = pd.to_datetime(sype['Date']).apply(lambda x: x.strftime('%Y-%m-%d'))

# Convertir todo los valores en 'PE-ratio' a int
sype['PE-ratio'] = sype['PE-ratio'].apply(lambda x: re.sub('[^\d.]+','', x))
sype['PE-ratio'] = sype['PE-ratio'].astype(float)

sype.to_csv('csv/sp500pe-ratio.csv', index = False)


#================== Empresas ======================


empresas500 = pd.read_csv("https://datahub.io/core/s-and-p-500-companies-financials/r/constituents-financials.csv")
total_market_cap = empresas500['Market Cap'].sum()
empresas500['% del S&P500'] = empresas500['Market Cap'] / total_market_cap * 100

empresas500.to_csv('csv/empresas_sp500.csv', index = False)