import requests
import pandas as pd
# Disable SSL Warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning
                         )
baseUrl = "https://localhost:5000/v1/api"


def confirmStatus():
    base_url = "https://localhost:5000/v1/api/"
    endpoint = "iserver/auth/status"
    
    auth_req = requests.get(url=base_url+endpoint,verify=False)
    print(auth_req)
    print(auth_req.text)
    
def initialize_session():
    request_url = f"{baseUrl}/iserver/auth/ssodh/init"
    json_content= {"publish":True,"compete":True}
    requests.post(url=request_url, json=json_content,verify=False)
    print("Session Initialized")
    
def get_account():
    request_url = f"{baseUrl}/portfolio/accounts"
    res = requests.get(url=request_url, verify=False)
    if res.status_code == 200:
        data = res.json()  # Extract JSON data from the response
        print(data)
    else:
        print(f"Failed to fetch account data: {res.status_code}")
        print(res.text)
    
    return [data['id'] for data in data]
def get_positions(account_id):

    request_url = f"{baseUrl}/portfolio/{account_id}/positions/0?direction=a&period=1W&sort=position&model=MyModel"
    res = requests.get(url=request_url, verify=False)
    if res.status_code == 200:
        data = res.json()  # Extract JSON data from the response
        df = pd.DataFrame(data)
        df.to_csv('ib/data/positions.csv')
    else:
        print(f"Failed to fetch account data: {res.status_code}")
        print(res.text)
    
    return data
if __name__ == "__main__":
    # confirmStatus()
    # initialize_session()
    # get_account()
    get_positions('U11570761')