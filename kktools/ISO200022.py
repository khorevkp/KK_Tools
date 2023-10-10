class Pain001:
    def __init__(self, file_name):

        try:
            with open(file_name, 'r') as file:
                data = file.read()
        except FileNotFoundError as e:
            print(f"File {file_name} not found!")
            raise

        data = data.replace(
            ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"',
            '')
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
        try:
            debtor_account = batch.xpath('.//DbtrAcct/Id/IBAN')[0].text
        except:
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

            country = payment.xpath('.//Ctry')

            if (len(country) > 0):
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

            payment_dict = {
                'Name': name,
                'Amount': float(amount),
                'Currency': currency,
                'Reference': reference,
                'Country': country,
                'Address': address
            }

            # adding to each individual batch header batch information (about payer and execution date)
            payment_dict.update(batch_header)

            payments_list.append(payment_dict)

        return payments_list

    def __str__(self):
        file_info = f'Number of batches: {self.batches_count} \n'
        file_info += f'Total number of payments: {self.total_payments_count}'
        return str(file_info)