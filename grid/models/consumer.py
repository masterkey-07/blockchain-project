import random
import logging
from .blockchain import blockchain_manager, AUTHORIZER_ADDRESS, AUTHORIZER_PRIVATE_KEY

logger = logging.getLogger(__name__)

class Consumer:
    def __init__(self, name: str, min_demand: float, max_demand: float, account: str, time_period: int = 1):
        self.name = name
        self.substations = set()
        self.min_demand = min_demand
        self.max_demand = max_demand
        self.time_period = time_period
        self.private_key = account
        self.current_demand = None
        self.account = blockchain_manager.get_account(account)

    def authorize(self):
        try:
            consumer_contract = blockchain_manager.contracts['CONSUMER']
            contract_function = consumer_contract.functions.addAuthorizedManager(self.account.address)
            tx_params = blockchain_manager.get_transaction_params(AUTHORIZER_ADDRESS)
            tx_params = contract_function.build_transaction(tx_params)
            receipt = blockchain_manager.send_transaction(tx_params, AUTHORIZER_PRIVATE_KEY)
            
            if receipt:
                logger.info(f"{self.name} authorized as consumer. Transaction hash: {receipt['transactionHash'].hex()}")
                self._approve_token_transfer()
            else:
                raise Exception(f"Failed to authorize {self.name} as consumer")
        except Exception as e:
            logger.error(f"Error in authorizing consumer: {e}")
            raise

    def _approve_token_transfer(self):
        try:
            energy_token_contract = blockchain_manager.contracts['ENERGY_TOKEN']
            consumer_contract = blockchain_manager.contracts['CONSUMER']
            tx = energy_token_contract.functions.approve(consumer_contract.address, 1_000_000_000_000_000).build_transaction(
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

    def reset(self):
        self.current_demand = None

    def connect_to_substation(self, substation):
        self.substations.add(substation)
        logger.info(f"{self.name} connected to substation {substation.name}")

    @property
    def quantity_of_substations(self):
        return len(self.substations)

    def _get_new_demand(self):
        return round(random.uniform(self.min_demand, self.max_demand) * self.time_period)

    def get_demand(self) -> float:
        if self.current_demand is None:
            self.current_demand = self._get_new_demand()
        return self.current_demand / len(self.substations) if self.substations else self.current_demand

    def consume_power(self, received: int):
        logger.info(f"{self.name} received {received} of {self.get_demand()} Wh")