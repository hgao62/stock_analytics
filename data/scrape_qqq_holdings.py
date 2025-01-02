import requests
import pandas as pd
from bs4 import BeautifulSoup

def scrape_qqq_holdings(url: str) -> pd.DataFrame:
    """
    Scrape the QQQ holdings from the given URL.
    
    Parameters:
        url (str): The URL to scrape.
    
    Returns:
        pd.DataFrame: DataFrame containing the QQQ holdings.
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from {url}, status code: {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', id='etf-holdings-table')
    
    if table is None:
        raise Exception("Failed to find the table with id 'etf-holdings-table'")
    
    # Extract the table headers
    headers = [th.text.strip() for th in table.find_all('th')]
    
    # Extract the table rows
    rows = []
    for tr in table.find_all('tr')[1:]:  # Skip the header row
        cells = [td.text.strip() for td in tr.find_all('td')]
        if cells:
            rows.append(cells)
    
    # Create a DataFrame
    df = pd.DataFrame(rows, columns=headers)
    return df

def main():
    url = "https://www.invesco.com/us/financial-products/etfs/holdings?audienceType=Investor&ticker=QQQ"
    try:
        df = scrape_qqq_holdings(url)
        df.to_csv('qqq_holdings.csv', index=False)
        print("QQQ holdings data has been saved to 'qqq_holdings.csv'")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
