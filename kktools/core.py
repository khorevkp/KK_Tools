import pandas as pd
import requests
import xml.etree.ElementTree as ET

def df_to_excel(file_name, df, worksheet_name="Sheet1", max_length=25):
    with pd.ExcelWriter(file_name, engine='xlsxwriter', datetime_format='dd/mm/yyyy') as writer:

        df.to_excel(writer, sheet_name=worksheet_name, index=False)
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