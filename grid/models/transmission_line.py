import logging
from .blockchain import blockchain_manager, AUTHORIZER_ADDRESS, AUTHORIZER_PRIVATE_KEY

logger = logging.getLogger(__name__)

class TransmissionLine:
    def __init__(self, name: str, account: str):
        self.name = name
        self.account = blockchain_manager.get_account(account)
        self.private_key = account

    def authorize(self):
        try:
            transmission_line_contract = blockchain_manager.contracts['TRANSMISSION_LINE']
            contract_function = transmission_line_contract.functions.addAuthorizedOperator(self.account.address)
            tx_params = blockchain_manager.get_transaction_params(AUTHORIZER_ADDRESS)
            tx_params = contract_function.build_transaction(tx_params)
            receipt = blockchain_manager.send_transaction(tx_params, AUTHORIZER_PRIVATE_KEY)
            
            if receipt:
                logger.info(f"{self.name} authorized as a transmission line. Transaction hash: {receipt['transactionHash'].hex()}")
                self._approve_token_transfer()
            else:
                raise Exception(f"Failed to authorize {self.name} as a transmission line")
        except Exception as e:
            logger.error(f"Error in authorizing transmission line: {e}")
            raise

    def _approve_token_transfer(self):
        try:
            energy_token_contract = blockchain_manager.contracts['ENERGY_TOKEN']
            transmission_line_contract = blockchain_manager.contracts['TRANSMISSION_LINE']
            tx = energy_token_contract.functions.approve(transmission_line_contract.address, 1_000_000_000_000_000).build_transaction(
                blockchain_manager.get_transaction_params(self.account.address)
            )
            receipt = blockchain_manager.send_transaction(tx, self.private_key)
            if receipt:
                logger.info(f"Token transfer approved for {self.name}. Transaction hash: {receipt['transactionHash'].hex()}")
            else:
                raise Exception("Failed to approve token transfer")
        except Exception as e:
            logger.error(f"Error in approving token transfer: {e}")
            raise

    def transmit(self, transmitted_power: int):
        logger.info(f"{self.name} transmitted {transmitted_power} Wh")
        return transmitted_power

    def record_transmission(self, substation_address: str, transmitted_power: int):
        try:
            transmission_line_contract = blockchain_manager.contracts['TRANSMISSION_LINE']
            tx = transmission_line_contract.functions.transmitEnergy(substation_address, round(transmitted_power)).build_transaction(
                blockchain_manager.get_transaction_params(self.account.address)
            )
            receipt = blockchain_manager.send_transaction(tx, self.private_key)
            if receipt:
                logger.info(f"{self.name} recorded transmission of {transmitted_power} Wh to substation. Transaction hash: {receipt['transactionHash'].hex()}")
            else:
                raise Exception("Failed to record power transmission")
        except Exception as e:
            logger.error(f"Error in recording power transmission: {e}")
            raise