import os
import json
from web3 import Web3
from web3.middleware import geth_poa_middleware

# Connect to the local Hardhat network
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)




# Contract ABIs and addresses
# Replace these with your actual contract ABIs and addresses
PRODUCER_ABI = None  # Add your Producer contract ABI here

with open('../blockchain/artifacts/contracts/Producer.sol/Producer.json', 'r') as file:
    contract_json = json.load(file)
    PRODUCER_ABI = contract_json['abi']

PRODUCER_ADDRESS = Web3.to_checksum_address('0x9fe46736679d2d9a65f0992f2272de9f3c7fa6e0')  # Add your deployed Producer contract address here

ENERGY_TOKEN_ABI = None  # Add your EnergyToken contract ABI here
ENERGY_TOKEN_ADDRESS = Web3.to_checksum_address('0x5fbdb2315678afecb367f032d93f642f64180aa3')  # Add your deployed EnergyToken contract address here

with open('../blockchain/artifacts/contracts/EnergyToken.sol/EnergyToken.json', 'r') as file:
    contract_json = json.load(file)
    ENERGY_TOKEN_ABI = contract_json['abi']

# Load contracts
producer_contract = w3.eth.contract(address=PRODUCER_ADDRESS, abi=PRODUCER_ABI)
energy_token_contract = w3.eth.contract(address=ENERGY_TOKEN_ADDRESS, abi=ENERGY_TOKEN_ABI)

# Robot's Ethereum account
ROBOT_PRIVATE_KEY = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'  # Set this as an environment variable
robot_account = w3.eth.account.from_key(ROBOT_PRIVATE_KEY)

def get_transaction_params(address):
    return {
        'from': address,
        'nonce': w3.eth.get_transaction_count(address),
    }

def send_transaction(transaction, private_key):
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt

def become_authorized_producer(authorizer_address, authorizer_private_key):
    # This function should be called by an account that's already authorized
    # to add new authorized producers
    tx = producer_contract.functions.addAuthorizedProducer(robot_account.address).build_transaction(
        get_transaction_params(authorizer_address)
    )
    receipt = send_transaction(tx, authorizer_private_key)
    print(f"Robot authorized as producer. Transaction hash: {receipt['transactionHash'].hex()}")

def connect_transmission_line(transmission_line_address):
    tx = producer_contract.functions.connectTransmissionLine(transmission_line_address).build_transaction(
        get_transaction_params(robot_account.address)
    )
    receipt = send_transaction(tx, ROBOT_PRIVATE_KEY)
    print(f"Transmission line connected. Transaction hash: {receipt['transactionHash'].hex()}")

def produce_energy(transmission_line_address, amount):
    tx = producer_contract.functions.produceEnergy(transmission_line_address, amount).build_transaction(
        get_transaction_params(robot_account.address)
    )
    receipt = send_transaction(tx, ROBOT_PRIVATE_KEY)
    print(f"Energy produced. Transaction hash: {receipt['transactionHash'].hex()}")

def check_energy_balance(address):
    balance = energy_token_contract.functions.balanceOf(address).call()
    print(f"Energy balance of {address}: {balance}")

# Usage example
if __name__ == "__main__":
    # Replace with the address and private key of an account that's already authorized
    AUTHORIZER_ADDRESS = "0x..."
    AUTHORIZER_PRIVATE_KEY = "0x..."
    
    # First, authorize the robot as a producer
    become_authorized_producer(AUTHORIZER_ADDRESS, AUTHORIZER_PRIVATE_KEY)
    
    # Now the robot can perform actions
    TRANSMISSION_LINE_ADDRESS = "0x..."  # Replace with actual transmission line address
    connect_transmission_line(TRANSMISSION_LINE_ADDRESS)
    
    # Produce some energy
    produce_energy(TRANSMISSION_LINE_ADDRESS, Web3.toWei(100, 'ether'))  # Produce 100 energy tokens
    
    # Check the balance
    check_energy_balance(TRANSMISSION_LINE_ADDRESS)