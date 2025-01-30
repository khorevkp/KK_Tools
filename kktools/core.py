import pandas as pd
import requests
import xml.etree.ElementTree as ET
from lxml import etree

def get_ecb_rates(currency, start_period):
    # please see description of request structure here: https://sdw-wsrest.ecb.europa.eu/help/

    entrypoint = 'https://sdw-wsrest.ecb.europa.eu/service/'
    resource = 'data'  # The resource for data queries is always 'data'
    flowRef = 'EXR'  # Dataflow describing the data that needs to be returned,
                    # exchange rates in this case
    key = 'D.' + currency + '.EUR.SP00.A'  # Defining the dimension values, D stands for daily,
    # followed by currency code, etc.
    parameters = {'startPeriod': start_period}

    request_url = entrypoint + resource + '/' + flowRef + '/' + key

    # Make the HTTP request
    response = requests.get(request_url, params = parameters)

    xml_data = response.text  # the data returned is in XML format, so we need to parse it
    root = ET.fromstring(xml_data)

    rate_list = []
    for k in range(2, len(root[1][0])):  # the data starts at xml-tree element root[1][0],
        # this can be checked by looking at received data in the browser
        date = root[1][0][k][0].attrib['value']
        rate = root[1][0][k][1].attrib['value']
        rate_list.append((date, rate))

    df = pd.DataFrame(rate_list)
    df.columns = ['date', 'rate_value']
    df['rate_value'] = pd.to_numeric(df['rate_value'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(inplace=True)

    return df

def get_last_ecb_rates():
    # please see description of request structure here: https://sdw-wsrest.ecb.europa.eu/help/

    entrypoint = 'https://sdw-wsrest.ecb.europa.eu/service/'
    resource = 'data'  # The resource for data queries is always'data'
    flowRef = 'EXR'  # Dataflow describing the data that needs to be returned,
    # exchange rates in this case
    key = 'D..EUR.SP00.A'  # Defining the dimension values, D stands for daily,
    # followed by currency code (. -thus all currencies in that case), etc.
    parameters = {'lastNObservations': 1}

    request_url = entrypoint + resource + '/' + flowRef + '/' + key

    # Make the HTTP request
    response = requests.get(request_url, params=parameters)

    xml_data = response.text  # the data returned is in XML format, so we need to parse it
    root = ET.fromstring(xml_data)
    rate_list = []

    for child in root[1]:
        rate_list.append((child[0][1].attrib['value'],
                          child[2][0].attrib['value'], child[2][1].attrib['value']))

    df = pd.DataFrame(rate_list)
    df.columns = ['currency', 'date', 'rate_value']

    df['rate_value'] = pd.to_numeric(df['rate_value'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    return df

def df_to_excel(file_name, df, worksheet_name="Sheet1", max_length=25):
    with pd.ExcelWriter(file_name, engine='xlsxwriter', datetime_format='dd/mm/yyyy') as writer:

        df.to_excel(writer, sheet_name=worksheet_name, index=False)
        if (len(df)>0):
            workbook = writer.book
            worksheet = writer.sheets[worksheet_name]
            worksheet.autofilter(0, 0, df.shape[0], df.shape[1] - 1)
            format_num = workbook.add_format({'num_format': '#,##0.00'})
            format_date = workbook.add_format({'num_format': 'mm/dd/yyyy'})
            k = 0
            for column in list(df.columns):
                series = df[column]
                max_len = max((
                    series.astype(str).map(len).max(),  # len of largest item
                    len(str(series.name))  # len of column name/header
                    )) + 1  # adding a little extra space
                max_len = min(max_len, max_length)  # we want to limit still the length of the column with max_length
                if df.dtypes[column] == 'float64':
                    worksheet.set_column(k, k, max_len, format_num)
                else:
                    worksheet.set_column(k, k, max_len)
                k = k + 1


def dfs_to_excel(file_name, df_list, max_length=25, sheet_names = []):
    with pd.ExcelWriter(file_name, engine='xlsxwriter', datetime_format='dd/mm/yyyy') as writer:

        s = 1
        workbook = writer.book
        format_num = workbook.add_format({'num_format': '#,##0.00'})
        format_date = workbook.add_format({'num_format': 'mm/dd/yyyy'})

        for df in df_list:
            if sheet_names:
                worksheet_name = sheet_names[s-1]
            else:
                worksheet_name = "Sheet" + str(s)
            s = s + 1
            df.to_excel(writer, sheet_name=worksheet_name, index=False)
            worksheet = writer.sheets[worksheet_name]
            if (len(df) > 0):
                worksheet.autofilter(0, 0, df.shape[0], df.shape[1]-1)
                k = 0
                for column in list(df.columns):
                    series = df[column]
                    max_len = max((
                        series.astype(str).map(len).max(),  # len of largest item
                        len(str(series.name))  # len of column name/header
                    )) + 1  # adding a little extra space
                    max_len = min(max_len, max_length)  # we want to limit still the length of the column with max_length
                    if df.dtypes[column] == 'float64':
                        worksheet.set_column(k, k, max_len, format_num)
                    else:
                        worksheet.set_column(k, k, max_len)
                    k = k + 1


# class Camt:
#     def __init__(self, file_name):
#
#         try:
#             with open(file_name, 'r') as file:
#                 data = file.read()
#         except FileNotFoundError as e:
#             print(f"File {file_name} not found!")
#             raise
#
#         data = data.replace(' xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02"', '')
#         data = bytes(data, 'utf-8')
#         parser = etree.XMLParser(recover=True, encoding='utf-8')
#         self.tree = etree.fromstring(data, parser)
#
#         self.definitions = {
#             'OPBD': 'Opening Booked balance',
#             'CLBD': 'Closing Booked balance',
#             'CLAV': 'Closing Available balance',
#             'PRCD': 'Previously Closed Booked balance',
#             'FWAV': 'Forward Available balance'}
#
#     def get_balances(self):
#         stmt_list = self.tree.xpath('.//Stmt')
#         all_bals_list = []
#         for stmt in stmt_list:
#             bals_list = self.get_balances_per_stmt(stmt)
#             AcctId = stmt.xpath('./Acct/Id/IBAN|./Acct/Id/Othr/Id')[0].text
#             for x in bals_list:
#                 x['AccountId'] = AcctId
#             all_bals_list += bals_list
#         return pd.DataFrame.from_dict(all_bals_list)
#
#     def get_balances_per_stmt(self, stmt):
#         bals = stmt.xpath('.//Bal')
#         bals_list = []
#         for bal in bals:
#             Code = bal.xpath('.//Cd')[0].text
#
#             try:
#                 Description = self.definitions[Code]
#             except:
#                 Description = 'Unknown code'
#
#             Amount = bal.xpath('.//Amt')[0].text
#             Amount = float(Amount)
#             CdtDbtInd = bal.xpath('.//CdtDbtInd')[0].text
#
#             Currency = bal.xpath('.//Amt/@Ccy')[0]
#
#             Date = bal.xpath('./Dt/Dt|./Dt/DtTm')[0].text
#
#             if CdtDbtInd == 'DBIT':
#                 Amount = -Amount
#
#             bal_dict = {
#                 'Amount': Amount,
#                 'Currency': Currency,
#                 'Code': Code,
#                 'Description': Description,
#                 'Dr/Cr': CdtDbtInd,
#                 'Date': Date}
#             bals_list.append(bal_dict)
#         return bals_list
#
#     def get_transactions(self):
#         stmt_list = self.tree.xpath('.//Stmt')
#         all_entries_list = []
#         for stmt in stmt_list:
#             entries_list = self.get_transactions_per_stmt(stmt)
#             AcctId = stmt.xpath('./Acct/Id/IBAN|./Acct/Id/Othr/Id')[0].text
#             for x in entries_list:
#                 x['AccountId'] = AcctId
#             all_entries_list += entries_list
#         return pd.DataFrame.from_dict(all_entries_list)
#
#     def get_transactions_per_stmt(self, stmt):
#         entries = stmt.xpath('./Ntry')
#         entries_list = []
#
#         for entry in entries:
#             nm = entry.xpath('.//Dbtr/Nm')
#             if len(nm) > 0:
#                 Debtor = nm[0].text
#             else:
#                 Debtor = ''
#
#             nm = entry.xpath('.//Cdtr/Nm')
#             if len(nm) > 0:
#                 Creditor = nm[0].text
#             else:
#                 Creditor = ''
#
#             Reference = ''
#
#             refs = entry.xpath('.//Ustrd')
#             if len(refs) > 0:
#                 for ref in refs:
#                     Reference += ref.text
#
#             Amount = entry.xpath('./Amt')[0].text
#             Amount = float(Amount)
#             Currency = entry.xpath('./Amt/@Ccy')[0]
#             CdtDbtInd = entry.xpath('./CdtDbtInd')[0].text
#
#             if CdtDbtInd == 'DBIT':
#                 Amount = -Amount
#             try:
#                 ValDt = entry.xpath('./ValDt/Dt')[0].text
#             except:
#                 ValDt = ''
#
#             try:
#                 BookgDt = entry.xpath('./BookgDt/Dt')[0].text
#             except:
#                 BookgDt = ''
#
#             entry_dict = {
#                 'Amount': Amount,
#                 'Currency': Currency,
#                 'Dr/Cr': CdtDbtInd,
#                 'Debtor': Debtor,
#                 'Creditor': Creditor,
#                 'Reference': Reference,
#                 'ValDt': ValDt,
#                 'BookgDt': BookgDt
#             }
#
#             entries_list.append(entry_dict)
#
#         return entries_list
#
#     def get_stats(self):
#         stmt_list = self.tree.xpath('.//Stmt')
#         stmts = []
#
#         for stmt in stmt_list:
#             stmt_info = {}
#             AcctId = stmt.xpath('./Acct/Id/IBAN|./Acct/Id/Othr/Id')[0].text
#             CreDtTm = stmt.xpath('./CreDtTm')[0].text
#             stmt_info['AccountId'] = AcctId
#             stmt_info['Statement created'] = CreDtTm
#             stmt_txs = pd.DataFrame.from_dict(self.get_transactions_per_stmt(stmt))
#             stmt_info['NoTxs'] = len(stmt_txs)
#             if len(stmt_txs) > 0:
#                 stmt_info['Net Amount'] = stmt_txs['Amount'].sum()
#             else:
#                 stmt_info['Net Amount'] = 0
#
#             stmts.append(stmt_info)
#
#         return pd.DataFrame.from_dict(stmts)
#
#     def __str__(self):
#         return str(self.get_stats())
