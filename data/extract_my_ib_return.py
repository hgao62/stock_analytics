

from pathlib import Path
import pandas as pd
from typing import Optional, List
PATH = Path('./ib/data/')

tfsa_account_file = Path('./ib/data/U9978141_positions.csv')
individual_account_file = Path('./ib/data/U11570761_positions.csv')


def load_positions()-> List[str]:
    tfsa_position = pd.read_csv(tfsa_account_file)
    individual_position = pd.read_csv(individual_account_file )
    combine = pd.concat([tfsa_position, individual_position])
    columns = ['acctId','contractDesc','position','currency','avgCost','assetClass']
    combine = combine[columns]
    combine = combine[combine['assetClass'] == 'STK']
    return combine['contractDesc'].unique().tolist()
    # total_pos = combine.groupby(['contractDesc','currency'])['position'].sum().reset_index(name='total_position')

print(load_positions())