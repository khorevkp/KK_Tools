# kktools


========

This library provides python tools for finance and treasury specialists.

## Installation

`pip install git+https://github.com/khorevkp/KK_Tools.git`

## Basic Usage

Importing history of EUR/GBP exchange rates since 2000-01-01 and exporting it to an excel file with pretty formatting

```
import kktools as kkt

df = kkt.get_ecb_rates("GBP", "2000-01-01")
kkt.df_to_excel("Historical_Rates.xlsx", df)
```

### License
MIT licensed. Check the [`LICENSE`](https://github.com/khorevkp/KK_Tools/blob/master/LICENSE) file for full details.
