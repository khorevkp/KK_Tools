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

## Basic Usage

Importing history of EUR/GBP exchange rates since 2000-01-01 and exporting it to an excel file with pretty formatting

```
import kktools as kkt

df = kkt.get_ecb_rates("GBP", "2000-01-01")
kkt.df_to_excel("Historical_Rates.xlsx", df)
```

### License
MIT licensed. Check the [`LICENSE`](https://github.com/khorevkp/KK_Tools/blob/master/LICENSE) file for full details.
