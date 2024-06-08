from lxml import etree
import pandas as pd
import os
import re


class Pain001:
    def __init__(self, file_name):

        try:
            with open(file_name, 'r', encoding='utf-8-sig') as file:
                data = file.read()
        except FileNotFoundError:
            print(f"File {file_name} not found!")
            raise

        data = re.sub('<Document[\S\s]*?>', '<Document>', data)
        data = bytes(data, 'utf-8')
        parser = etree.XMLParser(recover=True, encoding='utf-8')
        self._tree = etree.fromstring(data, parser)

        # list of all elements with batches
        batches = self._tree.xpath('.//PmtInf')
        self.batches_count = len(batches)

        self.all_payments = []
        for batch in batches:
            payments = self._get_payments_per_batch(batch)
            self.all_payments.extend(payments)

        self.total_payments_count = len(self.all_payments)

    def _process_batch_header(self, batch):
        execution_date = batch.xpath('.//ReqdExctnDt')[0].text
        debtor_name = batch.xpath('.//Dbtr/Nm')[0].text
        debtor_account = batch.xpath('.//DbtrAcct/Id/IBAN|.//DbtrAcct/Id/Othr/Id')

        if len(debtor_account) > 0:
            debtor_account = debtor_account[0].text
        else:
            debtor_account = ''
        return {'debtor_name': debtor_name, 'debtor_account': debtor_account, 'execution_date': execution_date}

    def _get_payments_per_batch(self, batch):

        # processing information related to the whole batch
        batch_header = self._process_batch_header(batch)

        # processing information for all individual payments in the batch
        payments = batch.xpath('.//CdtTrfTxInf')
        payments_list = []

        for payment in payments:
            amount = payment.xpath('.//InstdAmt')[0].text

            currency = payment.xpath('.//InstdAmt/@Ccy')[0]

            name = payment.xpath('.//Cdtr/Nm')[0].text

            creditor_account = payment.xpath('.//CdtrAcct/Id/IBAN|.//CdtrAcct/Id/Othr/Id')

            if len(creditor_account) > 0:
                creditor_account = creditor_account[0].text
            else:
                creditor_account = ''

            country = payment.xpath('.//Ctry')

            if len(country) > 0:
                country = country[0].text
            else:
                country = ''

            references = payment.xpath('.//RmtInf/Ustrd')
            reference = ''
            for ref in references:
                reference += ref.text
                reference += ' '

            addresses = payment.xpath('.//AdrLine')
            address = ''
            for addr in addresses:
                address += addr.text
                address += ' '

            end_to_end = payment.xpath('.//EndToEndId')
            if len(end_to_end) > 0:
                end_to_end = end_to_end[0].text
            else:
                end_to_end = ''

            BIC = payment.xpath('.//BIC')
            if len(BIC) > 0:
                BIC = BIC[0].text
            else:
                BIC = ''

            payment_dict = {
                'Name': name,
                'Amount': float(amount),
                'Currency': currency,
                'Reference': reference,
                'Creditor_account': creditor_account,
                'Country': country,
                'Address': address,
                'BIC': BIC,
                'EndToEndId': end_to_end
            }

            # adding to each individual batch header batch information (about payer and execution date)
            payment_dict.update(batch_header)

            payments_list.append(payment_dict)

        return payments_list

    def __str__(self):
        file_info = f'Number of batches: {self.batches_count} \n'
        file_info += f'Total number of payments: {self.total_payments_count}'
        return str(file_info)


class InvalidCamt53Exception(Exception):
    """Raised when file provided is not a valid CAMT 053 file"""
    pass

class Camt053:
    def __init__(self, file_name):

        self.DEFINITIONS = {'OPBD': 'Opening Booked balance',
                            'OPAV': 'Opening available balance',
                            'CLBD': 'Closing Booked balance',
                            'CLAV': 'Closing Available balance',
                            'PRCD': 'Previously Closed Booked balance',
                            'FWAV': 'Forward Available balance'}
        self.file_name = file_name

        try:
            with open(file_name, 'r') as file:
                data = file.read()
        except FileNotFoundError:
            print(f"File {file_name} not found!")
            raise

        data = re.sub('<Document[\S\s]*?>', '<Document>', data)
        data = bytes(data, 'utf-8')
        try:
            parser = etree.XMLParser(recover=True, encoding='utf-8')
            tree = etree.fromstring(data, parser)
        except:
            raise InvalidCamt53Exception('Could not parse as xml file')

        stmt_list = tree.xpath('.//Stmt')

        if len(stmt_list) == 0:
            raise InvalidCamt53Exception('Zero number of statements present in the file')

        self.statements_info = self._get_stmts_info(stmt_list)

        self.accounts_list = [{'Account_id': stmt['Account_id'],
                               'Account_owner': stmt['Account_owner']} for stmt in self.statements_info]

        self.transactions = self._get_transactions(stmt_list)

    def _process_stmt_header(self, stmt):
        stmt_header = self._stmt_header_main(stmt)
        bals_all = self._get_balances_per_stmt(stmt)
        stmt_header.update(bals_all)
        return stmt_header

    def _stmt_header_main(self, stmt):
        account_id = stmt.xpath('./Acct/Id/IBAN|./Acct/Id/Othr/Id')[0].text

        name = stmt.xpath('./Acct/Nm')
        if len(name) > 0:
            name = stmt.xpath('./Acct/Nm')[0].text
        else:
            name = ''

        stmt_id = stmt.xpath('./Id')[0].text
        stmt_header_main = {'Statement_id': stmt_id,
                            'Account_id': account_id,
                            'Account_owner': name}
        return stmt_header_main

    def _get_stmts_info(self, stmt_list):
        statements_info = []
        for stmt in stmt_list:
            stmt_info = self._process_stmt_header(stmt)
            stmt_summary = self._get_summary_per_stmt(stmt)
            stmt_info.update(stmt_summary)
            statements_info.append(stmt_info)

        return statements_info

    def _get_summary_per_stmt(self, stmt):
        transactions = self._get_transactions_per_stmt(stmt)
        tx_num = len(transactions)

        total_amount = sum([t['Amount'] for t in transactions])

        summary_dict = {'transaction_count': tx_num, 'total_amount': total_amount}
        return summary_dict

    def _get_balances_per_stmt(self, stmt):
        bals = stmt.xpath('.//Bal')
        bals_all = {}

        for bal in bals:
            Code = bal.xpath('.//Cd')[0].text
            try:
                Description = self.DEFINITIONS[Code]
            except:
                Description = 'Unknown code'

            amount = bal.xpath('.//Amt')[0].text
            amount = float(amount)

            CdtDbtInd = bal.xpath('.//CdtDbtInd')[0].text

            Currency = bal.xpath('.//Amt/@Ccy')[0]

            Date = bal.xpath('./Dt/Dt|./Dt/DtTm')[0].text

            if CdtDbtInd == 'DBIT':
                amount = -amount

            bal_dict = {'Amount_' + Code: amount,
                        'Currency_' + Code: Currency,
                        'Code_' + Code: Code,
                        'Description_' + Code: Description,
                        'CdtDbtInd_' + Code: CdtDbtInd,
                        'Date_' + Code: Date}

            bals_all.update(bal_dict)

        return bals_all

    def _get_transactions(self, stmt_list):
        all_entries_list = []
        for stmt in stmt_list:
            all_entries_list += self._get_transactions_per_stmt(stmt)
        return all_entries_list

    def _get_transactions_per_stmt(self, stmt):
        entries = stmt.xpath('./Ntry')

        stmt_header_main = self._stmt_header_main(stmt)

        entries_list = []

        for entry in entries:
            nm = entry.xpath('.//Dbtr/Nm')
            if len(nm) > 0:
                Debtor = nm[0].text
            else:
                Debtor = ''

            acct = entry.xpath('.//DbtrAcct/Id/IBAN|.//DbtrAcct/Id/Othr/Id')
            if len(acct) > 0:
                DebtorAccount = acct[0].text
            else:
                DebtorAccount = ''

            nm = entry.xpath('.//Cdtr/Nm')
            if len(nm) > 0:
                Creditor = nm[0].text
            else:
                Creditor = ''

            acct = entry.xpath('.//CdtrAcct/Id/IBAN|.//CdtrAcct/Id/Othr/Id')
            if len(acct) > 0:
                CreditorAccount = acct[0].text
            else:
                CreditorAccount = ''

            Reference = ''
            refs = entry.xpath('.//Ustrd')
            if len(refs) > 0:
                for ref in refs:
                    if ref.text is not None:
                        Reference += ref.text

            AddInfo = ''
            refs = entry.xpath('.//AddtlNtryInf')
            if len(refs) > 0:
                for ref in refs:
                    if ref.text is not None:
                        AddInfo += ref.text

            Amount = entry.xpath('./Amt')[0].text
            Amount = float(Amount)
            Currency = entry.xpath('./Amt/@Ccy')[0]
            CdtDbtInd = entry.xpath('./CdtDbtInd')[0].text

            if CdtDbtInd == 'DBIT':
                Amount = -Amount
            try:
                ValDt = entry.xpath('./ValDt/Dt')[0].text
            except:
                ValDt = ''

            try:
                BookgDt = entry.xpath('./BookgDt/Dt')[0].text
            except:
                BookgDt = ''

            entry_dict = {
                'Amount': Amount,
                'Currency': Currency,
                'Dr_Cr': CdtDbtInd,
                'Debtor': Debtor,
                'DebtorAccount': DebtorAccount,
                'Creditor': Creditor,
                'CreditorAccount': CreditorAccount,
                'Reference': Reference,
                'AddInfo': AddInfo,
                'ValDt': ValDt,
                'BookgDt': BookgDt
            }
            entry_dict.update(stmt_header_main)

            entries_list.append(entry_dict)

        return entries_list

    def __str__(self):
        file_info = f'File name: {self.file_name} \n'
        file_info += f'Accounts: {self.accounts_list} \n'
        file_info += f'Number of statements in the file: {len(self.statements_info)} \n'
        file_info += f'Total number of transactions: {len(self.transactions)}'
        return str(file_info)


def process_CAMT053_folder(folder_CAMT53):
    df_files = []
    df_statements = pd.DataFrame()
    df_transactions = pd.DataFrame()

    for file_path in os.listdir(folder_CAMT53):
        full_path = os.path.join(folder_CAMT53, file_path)
        if os.path.isfile(full_path):
            try:
                camt = Camt053(full_path)

                df_stmts_temp = pd.DataFrame(camt.statements_info)
                df_statements = pd.concat([df_statements, df_stmts_temp])

                df_trans_temp = pd.DataFrame(camt.transactions)
                df_transactions = pd.concat([df_transactions, df_trans_temp])

                file_dict = {'file': file_path,
                             'account_id': camt.accounts_list,
                             'status': 'CAMT053 parsing successful'}

                df_files.append(file_dict)

            except Exception as e:
                file_dict = {'file': file_path,
                             'account_id': '',
                             'status': f'CAMT053 parsing not successful, reason: {e}'}

                df_files.append(file_dict)

    df_files = pd.DataFrame(df_files)
    cols_to_drop = ['Currency_OPBD', 'Code_OPBD',
                    'Description_OPBD', 'CdtDbtInd_OPBD', 'Date_OPBD',
                    'Currency_CLBD', 'Code_CLBD', 'Description_CLBD', 'CdtDbtInd_CLBD',
                    'Date_CLBD', 'Currency_OPAV', 'Code_OPAV',
                    'Description_OPAV', 'CdtDbtInd_OPAV', 'Date_OPAV',
                    'Currency_FWAV', 'Code_FWAV', 'Description_FWAV', 'CdtDbtInd_FWAV',
                    'Date_FWAV', 'Currency_CLAV', 'Code_CLAV',
                    'Description_CLAV', 'CdtDbtInd_CLAV', 'Date_CLAV']

    df_statements = df_statements.drop(axis='columns', labels=cols_to_drop, errors='ignore')

    return df_files, df_statements, df_transactions
