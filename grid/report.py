import json
import logging
from datetime import datetime
from web3 import Web3
from models.blockchain import blockchain_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TransactionAnalyzer:
    def __init__(self):
        self.web3 = blockchain_manager.web3
        self.contracts = blockchain_manager.contracts

    def decode_transaction(self, contract, tx):
        try:
            func_obj, func_params = contract.decode_function_input(tx['input'])
            return func_obj.fn_name, func_params
        except Exception as e:
            logger.error(f"Error decoding transaction: {e}")
            return None, None

    def get_relevant_transactions(self):
        relevant_txs = []
        try:
            latest_block = self.web3.eth.get_block('latest')['number']
            
            for block_number in range(latest_block + 1):
                block = self.web3.eth.get_block(block_number, full_transactions=True)
                for tx in block['transactions']:
                    if tx['to'] in [self.contracts['PRODUCER'].address, self.contracts['ENERGY_TOKEN'].address, self.contracts['TRANSMISSION_LINE'].address, self.contracts['SUBSTATION'].address, self.contracts['CONSUMER'].address]:
                        func_name, func_params = self.decode_transaction(self.get_contract_for_address(tx['to']), tx)

                        if func_name:
                            logger.info(f"Found relevant transaction: {func_name}")

                            amount = func_params.get('amount', func_params.get('value', 0))
                            relevant_txs.append({
                                'transactionHash': tx['hash'],
                                'blockNumber': block_number,
                                'from': tx['from'],
                                'to': tx['to'],
                                'function': func_name,
                                'amount': amount,
                                'timestamp': block['timestamp']
                            })
            return relevant_txs
        except Exception as e:
            logger.error(f"Error getting relevant transactions: {e}")
            raise

    def get_contract_for_address(self, address):
        for contract in self.contracts.values():
            if contract.address == address:
                return contract
        return None

    def generate_html_table(self, transactions):
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Blockchain Transactions</title>
            <style>
                table {
                    border-collapse: collapse;
                    width: 100%;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
            </style>
        </head>
        <body>
            <h1>Blockchain Transactions</h1>
            <table>
                <tr>
                    <th>Transaction Hash</th>
                    <th>Block Number</th>
                    <th>From</th>
                    <th>To</th>
                    <th>Function</th>
                    <th>Amount</th>
                    <th>Timestamp</th>
                </tr>
        """

        for tx in transactions:
            timestamp = datetime.fromtimestamp(tx['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            amount = self.web3.from_wei(tx['amount'], 'ether')  # Convert from wei to ether for readability
            html += f"""
                <tr>
                    <td>{tx['transactionHash'].hex()}</td>
                    <td>{tx['blockNumber']}</td>
                    <td>{tx['from']}</td>
                    <td>{tx['to']}</td>
                    <td>{tx['function']}</td>
                    <td>{amount} EnergyTokens</td>
                    <td>{timestamp}</td>
                </tr>
            """

        html += """
            </table>
        </body>
        </html>
        """

        return html

    def analyze_and_generate_report(self):
        try:
            if not self.web3.is_connected():
                raise Exception("Not connected to Ethereum node")

            transactions = self.get_relevant_transactions()
            html_content = self.generate_html_table(transactions)

            with open('blockchain_transactions.html', 'w') as f:
                f.write(html_content)

            logger.info("HTML file generated: blockchain_transactions.html")
        except Exception as e:
            logger.error(f"Error in analyzing and generating report: {e}")
            raise

def main():
    try:
        analyzer = TransactionAnalyzer()
        analyzer.analyze_and_generate_report()
    except Exception as e:
        logger.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main()