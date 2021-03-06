# -*- coding: utf-8 -*-
"""Exploration.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10w-778E4QI3L6dILY3SVoIJnh-MO6_oP
"""

!git clone https://github.com/Marigold/universal-portfolios

!pip install universal-portfolios

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
# %load_ext autoreload
# %autoreload 2
# %config InlineBackend.figure_format = 'svg'

import numpy as np
import pandas as pd
import seaborn as sns
import datetime as dt
import matplotlib.pyplot as plt

import universal as up
from universal import tools, algos
from universal.algos import *

sns.set_context("notebook")
plt.rcParams["figure.figsize"] = (12, 7)

# load data using tools module
data = tools.dataset('nyse_o')

# plot first three of them as example
data.iloc[:,:3].plot()

"""# Première exploration

**Confidence weighted mean reversion strategy (cwmr)** modélise le veteur du portefeuille par une distribution gaussienne et met séquentiellement à jour le portefeuille en suivant le principe de retour à la moyenne.
"""

data = tools.dataset('nyse_o')
algo = algos.CWMR() 
result = algo.run(data)

#Affichage de quelques statistiques 
print(result.summary())

"""Le ratio de Sharpe est superieur à 3 ce qui prouve que la sur-performance ne se fait pas au prix d'un risque trop élevé. Alors l'allocation est parfaite."""

result.plot(weights=False, assets=False, ucrp=True, logy=True);

result.plot_decomposition(legend=False, logy=True);

"""La performance dépend surtout des 5 premiers actifs comme le montre le graphe ci-dessus.

# **Deuxième exploration**
"""

from pandas_datareader.data import DataReader

# Télechargement des données depuis yahoo
yahoo_data = DataReader(['AMZN' ,'IBM', 'AAPL', 'GOOG'], 'yahoo', start=dt.datetime(2017,1,1))['Adj Close']

yahoo_data.head()

#Ce qu'on peut gagner en moyenne en pourcentage
yahoo_data.pct_change().mean()

"""**Optimisation d'un portefeuille aléatoire** : Dans cette partie et en s'aidant d'internet, j'optimiserais un portefeuille aléatoire dans le but de comparer avec le ratio de sharpe déjà obtenu pour le portefeuille avec CWMR"""

import numpy as np
num_ports = 1500
log_ret = np.log(yahoo_data/yahoo_data.shift(1)) 
all_weights = np.zeros((num_ports,len(yahoo_data.columns)))
ret_arr = np.zeros(num_ports)
vol_arr = np.zeros(num_ports)
sharpe_arr = np.zeros(num_ports)

for p in range(num_ports):

    # Créer des poids aléatoires
    weights = np.array(np.random.random(4))

    # Pondération des poids
    weights = weights / np.sum(weights)
    
    # Sauvegarde des Poids
    all_weights[p,:] = weights

    # rendement attendu
    ret_arr[p] = np.sum((log_ret.mean() * weights) *252)

    # variance Attendue
    vol_arr[p] = np.sqrt(np.dot(weights.T, np.dot(log_ret.cov() * 252, weights)))

    # Ratio de Sharpe
    sharpe_arr[p] = ret_arr[p]/vol_arr[p]

"""**Optimisation**"""

from scipy.optimize import minimize

def get_value(weights):
    weights = np.array(weights)
    ret = np.sum(log_ret.mean() * weights) * 252
    vol = np.sqrt(np.dot(weights.T, np.dot(log_ret.cov() * 252, weights)))
    sr = ret/vol
    return np.array([ret,vol,sr])

def nsharpe(weights):
    return  get_value(weights)[2] * -1

def check_sum(weights):
    return np.sum(weights) - 1

cons = ({'type':'eq','fun': check_sum})
bounds = ((0, 1), (0, 1), (0, 1), (0, 1))
init_guess = [0.25,0.25,0.25,0.25]

opt_results = minimize(nsharpe,init_guess,method='SLSQP',bounds=bounds,constraints=cons)

get_value(opt_results.x)

"""Même après optimisation le ratio de Sharpe pour CWMR reste le meilleur.

# **Troisième exploration**
"""

mS = yahoo_data.resample('M').last()
wS = yahoo_data.resample('W').last()

result3 = algo.run(wS)
print(result3.summary())
result3.plot();
#On remarquera qu'il y a une forte fluctuation des poids

"""**Le drawdown** : Le drawdown est une mesure du risque de la stratégie. Une statistique intéressante pour connaître la performance de l'algorithme est le maximum drawdown. En effet, il représente la perte maximale d'une stratégie sur une période de temps qui vous permet de comprendre si la stratégie est risquée et donc de la choisir en fonction de votre niveau d'aversion au risque."""

result3.max_drawdown

result3.drawdown_period

algo = CRP()
result4 = algo.run(wS)
print(result4.max_drawdown)
print(result4.drawdown_period)

algo = PAMR()
result6 = algo.run(wS)
print(result6.max_drawdown)
print(result6.drawdown_period)

algo = RMR()
result5 = algo.run(wS)
print(result5.max_drawdown)
print(result5.drawdown_period)

"""CRP s'avère offrant le meilleur compromis entre valeur maximum et période de drawdown. 
CWMR reste l'algorithme qui prend une période asses longue ( entre les trois algorithmes alloués ) avec un risque aussi élevé .
"""