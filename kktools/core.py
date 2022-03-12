import pandas as pd

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