import json
from web3 import Web3
from web3.contract.contract import Contract
from web3.middleware import geth_poa_middleware
from web3.exceptions import InvalidAddress, ContractLogicError
from web3 import Account

def create_web3():
    web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    return web3

WEB3 = create_web3()

def get_contract(address, abi_path:str) -> Contract:
    file = open(abi_path, 'r')
    contract_json = json.load(file)
    abi = contract_json['abi']

    return WEB3.eth.contract(address=address, abi=abi)

def get_account(private_key) -> Account:
    return WEB3.eth.account.from_key(private_key)

def get_transaction_params(address):
    return {
        'from': address,
        'nonce': WEB3.eth.get_transaction_count(address),
        'gasPrice': WEB3.eth.gas_price,
        'chainId': WEB3.eth.chain_id,
    }

def send_transaction(transaction, private_key):
    try:
        signed_txn = WEB3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = WEB3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = WEB3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt
    except InvalidAddress as e:
        raise Exception(f"Invalid address in transaction: {e}")
    except ContractLogicError as e:
        raise Exception(f"Contract logic error: {e}")
    except Exception as e:
        raise Exception(f"Error sending transaction: {e}")
    return None

ENERGY_TOKEN_ADDRESS = Web3.to_checksum_address('0xc5a5C42992dECbae36851359345FE25997F5C42d')
energy_token_contract = get_contract(ENERGY_TOKEN_ADDRESS, "../blockchain/artifacts/contracts/EnergyToken.sol/EnergyToken.json")

CONSUMER_ADDRESS = Web3.to_checksum_address('0x67d269191c92Caf3cD7723F116c85e6E9bf55933')
consumer_contract = get_contract(CONSUMER_ADDRESS, "../blockchain/artifacts/contracts/Consumer.sol/Consumer.json")

PRODUCER_ADDRESS = Web3.to_checksum_address('0xE6E340D132b5f46d1e472DebcD681B2aBc16e57E')
producer_contract = get_contract(PRODUCER_ADDRESS, "../blockchain/artifacts/contracts/Producer.sol/Producer.json")

SUBSTATION_ADDRESS = Web3.to_checksum_address('0xc3e53F4d16Ae77Db1c982e75a937B9f60FE63690')
substation_contract = get_contract(SUBSTATION_ADDRESS, "../blockchain/artifacts/contracts/Substation.sol/Substation.json")

TRANSMISSION_LINE_ADDRESS = Web3.to_checksum_address('0x84eA74d481Ee0A5332c457a4d796187F6Ba67fEB')
transmission_line_contract = get_contract(TRANSMISSION_LINE_ADDRESS, "../blockchain/artifacts/contracts/TransmissionLine.sol/TransmissionLine.json")

AUTHORIZER_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"  
AUTHORIZER_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
