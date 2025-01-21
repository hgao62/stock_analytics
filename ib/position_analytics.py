import requests
import pandas as pd
# Disable SSL Warnings
import urllib3
import logging
from typing import List
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning
                         )
baseUrl = "https://localhost:5000/v1/api"

logging.basicConfig(
    filemode='a',
    filename='logs/interactive_brokers.log',  # Log file path
    level=logging.INFO,               # Log level
    format='%(asctime)s - %(levelname)s- %(filename)s:%(lineno)s  - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'       # Date format
)

class AccountID:
    INDIVIDUAL = 'U11570761'
    TFSA = 'U9978141'
    
def confirmStatus():
    base_url = "https://localhost:5000/v1/api/"
    endpoint = "iserver/auth/status"
    
    auth_req = requests.get(url=base_url+endpoint,verify=False)
    logging.info(f"Status Code: {auth_req.status_code}, auth_req.text: {auth_req.text}")
    
def initialize_session():
    request_url = f"{baseUrl}/iserver/auth/ssodh/init"
    json_content= {"publish":True,"compete":True}
    requests.post(url=request_url, json=json_content,verify=False)
    logging.info("Session Initialized")
    
def get_account()-> List[str]:
    request_url = f"{baseUrl}/portfolio/accounts"
    res = requests.get(url=request_url, verify=False)
    if res.status_code == 200:
        data = res.json()  # Extract JSON data from the response
    else:
        raise Exception(f"Failed to fetch account data: {res.status_code}")
    
    return [data['id'] for data in data]

def get_positions(account_id: str) ->None:

    request_url = f"{baseUrl}/portfolio/{account_id}/positions/0?direction=a&period=1W&sort=position&model=MyModel"
    res = requests.get(url=request_url, verify=False)
    if res.status_code == 200:
        data = res.json()  # Extract JSON data from the response
        df = pd.DataFrame(data)
        df.to_csv(f'ib/data/{account_id}_positions.csv')
    else:
        print(f"Failed to fetch account data: {res.status_code}")
        print(res.text)
    
    return data

def get_pnl():
    request_url = f"{baseUrl}/iserver/account/pnl/partitioned"
    res = requests.get(url=request_url, verify=False)
    if res.status_code == 200:
        data = res.json()  # Extract JSON data from the response
        idividual_account_pnl = data['upnl']['U11570761.']
        # tfsa_account_pnl = data['U9978141.']
        df = pd.DataFrame(idividual_account_pnl,index=[0])
        df = df.rename(columns={'date':'Date','dpl':'Daily PnL','upl':'Unrealized PnL','nl':'Net Liquidity'})
        df['account_no'] = 'U11570761'
        df.to_csv(f'ib/data/pnl.csv')
    else:
        print(f"Failed to fetch account data: {res.status_code}")
        print(res.text)
    
def switch_account(account_id: AccountID)->None:
    request_url = f"{baseUrl}/iserver/account"
    json_content = {"acctId": account_id}
    res = requests.post(url=request_url, json=json_content)
    if res.status_code == 200:
        data = res.json() 
        account_id = data['accId']
        logging.info(f"Switched to account: {account_id}")
    else:
        logging.error(f"Failed to switch account: {res.status_code}")
        logging.error(res.text)

def get_portfolio_allocation(account_id: AccountID)->None:
    request_url = f"{baseUrl}/portfolio/{account_id}/allocation"
    res = requests.get(url=request_url, verify=False)
    if res.status_code == 200:
        data = res.json()
        
        # Extract and format data for asset class, sector, and group
        allocation_types = ['assetClass', 'sector', 'group']
        for allocation_type in allocation_types:
            allocation_data = data[allocation_type]['long']
            allocation_data= [{allocation_type: k, 'amount': v} for k, v in allocation_data.items()]
     
        # Save data to CSV files
            pd.DataFrame(allocation_data).to_csv(f'ib/data/{account_id}_{allocation_type}_allocation.csv', index=False)
          
        logging.info(f"Portfolio allocation data for account {account_id} saved successfully.")
    else:
        logging.error(f"Failed to fetch account data: {res.status_code}")
        logging.error(res.text) 

def get_account_performance(account_id:AccountID, period:str)->None:
        """Available Values: 1D,7D,MTD,1M,YTD,1Y"""
        request_url = f"{baseUrl}/pa/performance"
        json_content = {"acctIds": [account_id],"period": "1Y"}
        
        res = requests.post(url=request_url, json=json_content,verify=False)
        
        
        if res.status_code == 200:
            data = res.json()
            types = ['nav','cps'] 
            data_nav = data['nav']['data'][0]['navs']
            data_cum_return = data['cps']['data'][0]['returns']
            type_dates = data['nav']['dates']
            df = pd.DataFrame({
                'Date': type_dates,
                'Net present value': data_nav,
                'Cumulative performance data': data_cum_return
            })
            df.to_csv(f'ib/data/{account_id}_{period}_performance.csv', index=False)
        
        
def get_transactions(account_id:AccountID)->None:
    request_url = f"{baseUrl}/portfolio/{account_id}/transactions"
       
    res = requests.post(url=request_url,verify=False)
    if res.status_code == 200:
        data = res.json()
    
def main()->None:
    confirmStatus()
    initialize_session()
    accounts = get_account()
    for account in accounts:
        get_positions(account)

if __name__ == "__main__":
    # main()
    # get_pnl()
    # get_portfolio_allocation(AccountID.INDIVIDUAL)
    # get_account_performance(account_id=AccountID.TFSA, period='2Y')
    get_transactions(AccountID.INDIVIDUAL)