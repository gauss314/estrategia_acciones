import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import copy
import datetime as dt

# IMPORTACION DE DATOS========================================================

tickers = ["GGAL", "BMA", "YPF", "PAM", "TGS", "CRESY", "IRS", "TEO",
           "MELI", "EDN", "BBAR", "CEPU", "TX", "SUPV", "LOMA"]


weekly_ret = {}
años = 10
start = dt.date.today()-dt.timedelta(365*años)
end = dt.date.today()


for i in range(len(tickers)):
    weekly_ret[tickers[i]] = yf.download(tickers[i], start=start, end=end, interval="1wk")


#CALCULO RETORNO SEMANAL=======================================================

tickers_dir = copy.deepcopy(weekly_ret)
returns = pd.DataFrame()

for ticker in tickers:
    print(f"calculating return for {ticker}")
    tickers_dir[ticker]["weekly_ret"] = tickers_dir[ticker]["Close"].pct_change()
    returns[ticker] = tickers_dir[ticker]["weekly_ret"]

#returns.dropna(inplace=True)


#CALCULO ESTRATEGIA LONG REZAGADOS=============================================

def estrategia (DF, m, x):
    "m: cuantas acciones mantengo semanalmente"
    "x: cuantas acciones reemplazo semanalmente"
    df = DF.copy()
    portfolio = []
    weekly_return = [0]
    for i in range(1, len(df)):
        if len(portfolio) > 0:
            weekly_return.append(df[portfolio].iloc[i,:].mean())
            subieron_mucho = df[portfolio].iloc[i,:].sort_values(ascending=False)[:x].index.values.tolist()
            portfolio = [t for t in portfolio if t not in subieron_mucho]
        fill = m - len(portfolio)
        new_pics = df[[t for t in tickers if t not in portfolio]].iloc[i,:].sort_values(ascending=True)[:fill].index.values.tolist()
        portfolio = portfolio + new_pics
        print(portfolio)
    weekly_return_df = pd.DataFrame(weekly_return, columns=["weekly_return"])
    return weekly_return_df

#CALCULO ESTRATEGIA LONG CALIENTES=============================================
    
def pflio(DF,m,x):
    "m: cuantas acciones mantengo semanalmente"
    "x: cuantas acciones reemplazo semanalmente"
    df = DF.copy()
    portfolio = []
    weekly_return = [0]
    for i in range(1,len(df)):
        if len(portfolio) > 0:
            weekly_return.append(df[portfolio].iloc[i,:].mean())
            bad_stocks = df[portfolio].iloc[i,:].sort_values(ascending=True)[:x].index.values.tolist()
            portfolio = [t for t in portfolio if t not in bad_stocks]
        fill = m - len(portfolio)
        #Variante: se puede sacar de abajo el [[t for t in tickers if t not in portfolio]] para repetir acciones
        new_picks = df[[t for t in tickers if t not in portfolio]].iloc[i,:].sort_values(ascending=False)[:fill].index.values.tolist()
        portfolio = portfolio + new_picks
        print(portfolio)
    weekly_ret_df = pd.DataFrame(weekly_return,columns=["weekly_return"])
    return weekly_ret_df


#CALCULO KPIs==================================================================
def CAGR(DF):
    df = DF.copy()
    df["cum_return"] = (1 + df["weekly_return"]).cumprod()
    n = len(df)/52
    CAGR = (df["cum_return"].tolist()[-1])**(1/n) - 1
    return CAGR

def volatility(DF):
    df = DF.copy()
    vol = df["weekly_return"].std() * np.sqrt(52)
    return vol 

def max_dd(DF):
    df = DF.copy()
    df["cum_return"] = (1 + df["weekly_return"]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd
# =============================================================================
#               TEST DE KPIs
# =============================================================================

a = CAGR(estrategia(returns, 1, 1))
b = CAGR(estrategia(returns, 5, 5))
c = CAGR(estrategia(returns, 15, 15))
d = CAGR(pflio(returns, 1, 1))
e = CAGR(pflio(returns, 5, 5))

f = volatility(estrategia(returns, 1, 1))
g = volatility(estrategia(returns, 5, 5))
h = volatility(estrategia(returns, 15, 15))
i = volatility(pflio(returns, 1, 1))
j = volatility(pflio(returns, 5, 5))

k = max_dd(estrategia(returns, 1, 1))
l = max_dd(estrategia(returns, 5, 5))
m = max_dd(estrategia(returns, 15, 15))
n = max_dd(pflio(returns, 1, 1))
o = max_dd(pflio(returns, 5, 5))

datos = {"CAGR": [a, b, c, d, e],
         "Volatilidad": [f, g, h, i, j],
         "perdida_max": [k, l , m, n, o]}

data = pd.DataFrame(datos)
data = data.T
data.rename(columns={0:"peor",
                     1:"5 peores",
                     2:"todas",
                     3:"mejor",
                     4:"5 mejores"}, inplace=True)

# SETEO TAMAÑO Y ESTILO DEL GRAFICO

plt.rcParams["figure.figsize"]=[10,5]
plt.style.use("dark_background")

# GRAFICO

plt.plot((1+estrategia(returns, 5, 5)).cumprod(), c="b", label="comprar las 5 que menos subieron")
plt.plot((1+estrategia(returns, 1, 1)).cumprod(), c="w", label="comprar la que menos subió")
plt.plot((1+estrategia(returns, 15, 15)).cumprod(), c="r", label="buy and hold todas")
plt.plot((1+pflio(returns, 1, 1)).cumprod(), label="comprar la que + subió")
plt.plot((1+pflio(returns, 5, 5)).cumprod(), label="comprar las 5 que + subieron")
plt.title("15 acciones en total - rebalanceo semanal [Incluye MELI]")
plt.ylabel("retorno acumulado en u$s")
plt.xlabel("semanas")
plt.legend()










