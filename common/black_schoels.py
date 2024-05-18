import numpy as np
import scipy.stats as st

def option_price(S: float, K: float, r: float, vol: float, dt: float, cp: str):
    if cp == 'C':
        return K*st.norm.cdf(-d2(S,K,r,vol,dt))*np.exp(-r*(dt))-S*st.norm.cdf(-d1(S,K,r,vol,dt))
    else:
        return S*st.norm.cdf(d1(S,K,r,vol,dt))-K*np.exp(-r*(dt))*st.norm.cdf(d2(S,K,r,vol,dt))

def delta(S: float, K: float, r: float, vol: float, dt: float, cp: str = 'C'):
    if cp == 'C':
        return st.norm.cdf(d1(S,K,r,vol,dt))
    else:
        return st.norm.cdf(d1(S,K,r,vol,dt)) - 1

def vega(S: float, K: float, r: float, vol: float, dt: float):
    return S*np.sqrt(dt)/np.sqrt(2*np.pi)*np.exp(-0.5*d1(S,K,r,vol,dt)**2)

def gamma(S: float, K: float, r: float, vol: float, dt: float):
    return 1/(vol*S*np.sqrt(2*dt*np.pi))*np.exp(-0.5*d1(S,K,r,vol,dt)**2)

def d1(S: float, K: float, r: float, vol: float, dt: float):
    return (np.log(S/K)+(r+vol**2/2)*(dt))/(vol*np.sqrt(dt))

def d2(S: float, K: float, r: float, vol: float, dt: float):
    return (np.log(S/K)+(r-vol**2/2)*(dt))/(vol*np.sqrt(dt))