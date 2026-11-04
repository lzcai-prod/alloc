import pickle, numpy as np, pandas as pd
from model import *
D=pickle.load(open(SP+'report/opts.pkl','rb'))
OPT,RES,SC,LR,GRID,HOLD,DEPLOY,BUFFER,ACCT_CASH,TM,T0=[D[k] for k in ['OPT','RES','SC','lr','grid','hold','DEPLOY','BUFFER','acct_cash','tm','t0']]

LABEL={'US_EQ':'US equity','US_THEME':'US thematic (XBI, XLP)','INTL_DM':'Intl developed equity','EM_EQ':'EM equity','SG_EQ':'Singapore equity','REAL_ESTATE':'Real estate (VNQ)','COMMOD':'Commodities','GOLD':'Gold','CRYPTO':'Bitcoin','ALLW':'ALLW (multi-asset)','CREDIT':'Credit','CORE_BONDS':'Core bonds','CASH (IBKR)':'Cash (IBKR)'}
