import json
import logging
from web3 import Web3, Account
from web3.contract.contract import Contract
from web3.middleware import geth_poa_middleware
from web3.exceptions import InvalidAddress, ContractLogicError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BlockchainManager:
    def __init__(self, provider_url='http://127.0.0.1:8545'):
        self.web3 = self._create_web3(provider_url)
        self.contracts = {}
        self._load_contracts()

    def _create_web3(self, provider_url):
        web3 = Web3(Web3.HTTPProvider(provider_url))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        return web3

    def _load_contracts(self):
        contract_info = {
            'ENERGY_TOKEN': ('0xc5a5C42992dECbae36851359345FE25997F5C42d', "../blockchain/artifacts/contracts/EnergyToken.sol/EnergyToken.json"),
            'CONSUMER': ('0x67d269191c92Caf3cD7723F116c85e6E9bf55933', "../blockchain/artifacts/contracts/Consumer.sol/Consumer.json"),
            'PRODUCER': ('0xE6E340D132b5f46d1e472DebcD681B2aBc16e57E', "../blockchain/artifacts/contracts/Producer.sol/Producer.json"),
            'SUBSTATION': ('0xc3e53F4d16Ae77Db1c982e75a937B9f60FE63690', "../blockchain/artifacts/contracts/Substation.sol/Substation.json"),
            'TRANSMISSION_LINE': ('0x84eA74d481Ee0A5332c457a4d796187F6Ba67fEB', "../blockchain/artifacts/contracts/TransmissionLine.sol/TransmissionLine.json"),
        }

        for name, (address, abi_path) in contract_info.items():
            self.contracts[name] = self._get_contract(address, abi_path)

    def _get_contract(self, address, abi_path) -> Contract:
        with open(abi_path, 'r') as file:
            contract_json = json.load(file)
        abi = contract_json['abi']
        return self.web3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)

    def get_account(self, private_key) -> Account:
        return self.web3.eth.account.from_key(private_key)

    def get_transaction_params(self, address):
        return {
            'from': address,
            'nonce': self.web3.eth.get_transaction_count(address),
            'gasPrice': self.web3.eth.gas_price,
            'chainId': self.web3.eth.chain_id,
        }

    def send_transaction(self, transaction, private_key):
        try:
            signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            logger.info(f"Transaction sent successfully. Hash: {tx_receipt['transactionHash'].hex()}")
            return tx_receipt
        except InvalidAddress as e:
            logger.error(f"Invalid address in transaction: {e}")
            raise
        except ContractLogicError as e:
            logger.error(f"Contract logic error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error sending transaction: {e}")
            raise

# Global instance of BlockchainManager
blockchain_manager = BlockchainManager()

# Constants
AUTHORIZER_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
AUTHORIZER_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"