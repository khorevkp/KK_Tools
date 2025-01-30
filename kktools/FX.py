import pandas as pd
from lxml import etree
import shutil
import os
import datetime

def extract_trades_and_save_FIS(source_path, archive_folder, output_path, company_code, BU_DICT, CP_DICT):
    swaps, forwards = extract_360T_trades(source_path, archive_folder, company_code, BU_DICT, CP_DICT)
    df_forwards = pd.DataFrame()
    df_swaps = pd.DataFrame()
    for forward in forwards:
        df_forwards = pd.concat([df_forwards, forward.convert_to_FIS()])
    for swap in swaps:
        df_swaps = pd.concat([df_swaps, swap.convert_to_FIS()])

    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    if len(df_forwards) > 0:
        df_forwards.to_excel(output_path + r'/' + current_time + '_forwards.xlsx',
                             startrow=3, sheet_name='Spot_Fwd', index=False)
    if len(df_swaps) > 0:
        df_swaps.to_excel(output_path + r'/' + current_time + '_swaps.xlsx',
                          startrow=3, sheet_name='Swap', index=False)
    return df_forwards, df_swaps


class Trade360T:
    FIS_FWD_COLUMNS = ['Spot/Forward',
                       'Business Unit',
                       'Counterparty',
                       'Deal Type',
                       'Deal Date',
                       'Value Date',
                       'Buy/Sell',
                       'Buy Currency',
                       'Sell Currency',
                       'Amount',
                       'Spot Rate',
                       'Fwd Points',
                       'Fwd Rate',
                       '360T Reference']

    FIS_SWP_COLUMNS = ['Business Unit',
                       'Counterparty',
                       'Deal Type',
                       'Trade Date',
                       'Buy/Sell',
                       'Buy Currency',
                       'Sell Currency',
                       'NL-Value Date',
                       'NL-Amount',
                       'NL-Spot Rate',
                       'NL-Forward Points',
                       'NL-Forward Rate',
                       'FL-Value Date',
                       'FL-Amount',
                       'FL-Spot Rate',
                       'FL-Forward Points',
                       'FL-Forward Rate',
                       '360T Reference']

    def __init__(self, file_name, company_code, BU_DICT, CP_DICT):
        self.company_code = company_code
        self.tree = self.get_tree_from_file(file_name)
        self.data = self.get_data_from_tree()
        self.type = self.data['product_name']
        self.id = self.data['reference_id']
        self.BU_DICT = BU_DICT
        self.CP_DICT = CP_DICT

    def get_tree_from_file(self, file_name):
        try:
            with open(file_name, 'r') as file:
                data = file.read()
                data = bytes(data, 'utf-8')
                parser = etree.XMLParser(recover=True, encoding='utf-8')
                tree = etree.fromstring(data, parser)
                return tree
        except FileNotFoundError as e:
            print(f"File {file_name} not found!")
            raise

    def get_data_from_tree(self):
        product = self.tree.xpath('.//product')[0].getchildren()[0]
        product_name = product.tag
        data_dict = {'product_name': product_name}
        data_dict['BU'] = self.company_code

        trade_date = self.tree.xpath('.//tradeDate')[0].text[:10]
        data_dict['trade_date'] = trade_date

        reference_id = self.tree.xpath('.//referenceId')[0].text[:10]
        data_dict['reference_id'] = reference_id

        if product_name == 'fxOutright':
            data_dict = self.process_fwd(product, data_dict, '')

        if product_name == 'fxSwap':
            near_leg = self.tree.xpath('.//product/fxSwap/fxNearLeg')[0]
            data_dict = self.process_fwd(near_leg, data_dict, '_near_leg')

            far_leg = self.tree.xpath('.//product/fxSwap/fxFarLeg')[0]
            data_dict = self.process_fwd(far_leg, data_dict, '_far_leg')

        return data_dict

    def process_fwd(self, product, data_dict_gen, add_on):
        data_dict = {}

        buyer = product.xpath('./buyer')[0].text
        seller = product.xpath('./seller')[0].text
        vd = product.xpath('./effectiveDate')[0].text

        currency_buyer = product.xpath('./currency1')[0].text
        currency_seller = product.xpath('./currency2')[0].text

        spot = float(product.xpath('./referenceSpotRate')[0].text)
        fwdpnts = float(product.xpath('./forwardPoints')[0].text)
        rate = float(product.xpath('./outrightRate')[0].text)

        data_dict['spot'] = spot
        data_dict['fwdpnts'] = fwdpnts
        data_dict['rate'] = rate
        data_dict['vd'] = vd

        notional_currency = product.xpath('./notionalCurrency')[0].text
        notional_amount = product.xpath('./notionalAmount')[0].text
        opposite_amount = product.xpath('./oppositeAmount')[0].text

        if buyer == self.company_code:
            data_dict['Counterparty'] = seller
            buy_currency = currency_buyer
            sell_currency = currency_seller

            if currency_buyer == notional_currency:
                direction = 'Buy'
            else:
                direction = 'Sell'
        else:
            data_dict['Counterparty'] = buyer
            buy_currency = currency_seller
            sell_currency = currency_buyer

            if currency_seller == notional_currency:
                direction = 'Buy'
            else:
                direction = 'Sell'

        data_dict['direction'] = direction
        data_dict['currency'] = notional_currency

        data_dict['buy_currency'] = buy_currency
        data_dict['sell_currency'] = sell_currency

        data_dict['amount'] = float(notional_amount)
        data_dict['opposite_amount'] = float(opposite_amount)

        data_dict = {k + add_on: v for k, v in data_dict.items()}

        return {**data_dict_gen, **data_dict}

    def convert_to_FIS(self):
        df_deal = pd.DataFrame.from_dict([self.data])
        if self.type == 'fxOutright':
            df_deal['FIS_deal_type'] = 'FXFWEXT'
            cols = ['product_name', 'BU', 'Counterparty', 'FIS_deal_type', 'trade_date', 'vd', 'direction',
                    'buy_currency',
                    'sell_currency', 'amount', 'spot', 'fwdpnts', 'rate', 'reference_id']

            df_deal['vd'] = df_deal['vd'].apply(self.process_date)
            df_deal['trade_date'] = df_deal['trade_date'].apply(self.process_date)

            df_deal['BU'] = df_deal['BU'].map(self.BU_DICT)
            df_deal['Counterparty'] = df_deal['Counterparty'].map(self.CP_DICT)

            df_deal['product_name'] = 'F'

            df_deal = df_deal[cols]
            df_deal.columns = self.FIS_FWD_COLUMNS

        elif self.type == 'fxSwap':
            df_deal['FIS_deal_type'] = 'FXSWEXT'
            cols = ['BU', 'Counterparty_near_leg', 'FIS_deal_type', 'trade_date',
                    'direction_near_leg', 'buy_currency_near_leg', 'sell_currency_near_leg',
                    'vd_near_leg', 'amount_near_leg', 'spot_near_leg', 'fwdpnts_near_leg', 'rate_near_leg',
                    'vd_far_leg', 'amount_far_leg', 'spot_far_leg', 'fwdpnts_far_leg', 'rate_far_leg', 'reference_id']

            df_deal['vd_near_leg'] = df_deal['vd_near_leg'].apply(self.process_date)
            df_deal['vd_far_leg'] = df_deal['vd_far_leg'].apply(self.process_date)
            df_deal['trade_date'] = df_deal['trade_date'].apply(self.process_date)

            df_deal['BU'] = df_deal['BU'].map(self.BU_DICT)
            df_deal['Counterparty_near_leg'] = df_deal['Counterparty_near_leg'].map(self.CP_DICT)

            df_deal = df_deal[cols]
            df_deal.columns = self.FIS_SWP_COLUMNS

        else:
            df_deal = None

        return df_deal

    @staticmethod
    def process_date(date):
        year = date[0:4]
        month = date[5:7]
        day = date[8:10]
        return day + '/' + month + '/' + year

    def __str__(self):
        pretty_str = [k + ': ' + str(self.data[k]) + '\n' for k in self.data.keys()]
        return ''.join(pretty_str)

    def __repr__(self):
        return 'Trade ID ' + self.id + ': ' + self.type


def extract_360T_trades(source_path, archive_folder, company_code, BU_DICT=[], CP_DICT=[]):
    swaps = []
    forwards = []

    for file_name in os.listdir(source_path):
        # check if current file_path is a file
        file_path = os.path.join(source_path, file_name)
        if os.path.isfile(file_path):
            try:
                trade = Trade360T(file_path, company_code, BU_DICT, CP_DICT)
                if trade.type == 'fxOutright':
                    forwards.append(trade)
                if trade.type == 'fxSwap':
                    swaps.append(trade)

                shutil.move(file_path,
                            os.path.join(archive_folder, file_name))
            except:
                print(f'\n Could not parse file: {file_name}')
    return swaps, forwards