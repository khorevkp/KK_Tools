# kktools


========

This library provides python tools for finance and treasury specialists.

## Installation

`pip install kktools`

## Realized Functionality
`get_ecb_rates("CUR", "YYYY-MM-DD")` - returns pandas dataframe with historical values for a given currency ("CUR") starting from the given date.  
`get_last_ecb_rates()` - returns pandas dataframe with the latest valid ECB exchange rates for all published currencies.  
`df_to_excel("file_name.xlsx", dataframe)` - exports pandas dataframe to an excel file with pretty formatting.  
`dfs_to_excel("file_name.xlsx", list_of_dataframes)` - exports list of pandas dataframes to an excel file with pretty formatting.  
`Camt` - class for parsing CAMT053 files (EOD bank statements, ISO20022 standard)

## Basic Usage

Importing history of EUR/GBP exchange rates since 2000-01-01 and exporting it to an excel file with pretty formatting

```
import kktools as kkt

df = kkt.get_ecb_rates("GBP", "2000-01-01")
kkt.df_to_excel("Historical_Rates.xlsx", df)
```

Parsing CAMT053 file and getting list of balances and list of all transactions:
```
from kktools import Camt

camt = Camt(file_name) # to create an object of Camt class you need to pass path+file_name of the CAMT053 file to be processed
camt.get_balances() # return pandas dataframe with all the balances (OPBD/CLBD/CLAV/PRCD/FWAV) for each statement in the file
camt.get_transactions() # return pandas dataframe with all the transactions in the file.
# For each balance and transaction the related statement will be designated by AccountId column

```

### License
MIT licensed. Check the [`LICENSE`](https://github.com/khorevkp/KK_Tools/blob/master/LICENSE) file for full details.
