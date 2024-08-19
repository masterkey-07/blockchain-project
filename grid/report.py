from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
from datetime import datetime
from models.blockchain import *

# Ensure we're connected
if not WEB3.is_connected():
    raise Exception("Not connected to Ethereum node")

# Contract addresses
def decode_transaction(contract, tx):
    try:
        func_obj, func_params = contract.decode_function_input(tx['input'])
        return func_obj.fn_name, func_params
    except:
        return None, None

def get_relevant_transactions():
    relevant_txs = []
    latest_block = WEB3.eth.get_block('latest')['number']
    
    for block_number in range(latest_block + 1):
        block = WEB3.eth.get_block(block_number, full_transactions=True)
        for tx in block['transactions']:
            if tx['to'] in [PRODUCER_ADDRESS, ENERGY_TOKEN_ADDRESS, TRANSMISSION_LINE_ADDRESS]:
                if tx['to'] == PRODUCER_ADDRESS:
                    func_name, func_params = decode_transaction(producer_contract, tx)
                elif tx['to'] == TRANSMISSION_LINE_ADDRESS:
                    func_name, func_params = decode_transaction(transmission_line_contract, tx)
                else:
                    func_name, func_params = decode_transaction(energy_token_contract, tx)

                print(func_name)

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

def generate_html_table(transactions):
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
        amount = WEB3.from_wei(tx['amount'], 'ether')  # Convert from wei to ether for readability
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

# Fetch relevant transactions
transactions = get_relevant_transactions()

# Generate HTML
html_content = generate_html_table(transactions)

# Write HTML to file
with open('blockchain_transactions.html', 'w') as f:
    f.write(html_content)

print("HTML file generated: blockchain_transactions.html")