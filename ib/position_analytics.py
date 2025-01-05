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

def main()->None:
    confirmStatus()
    initialize_session()
    accounts = get_account()
    for account in accounts:
        get_positions(account)

if __name__ == "__main__":
    main()