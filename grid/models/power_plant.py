import logging
from .blockchain import blockchain_manager, AUTHORIZER_ADDRESS, AUTHORIZER_PRIVATE_KEY

logger = logging.getLogger(__name__)

class PowerPlant:
    def __init__(self, name: str, max_output: int, account: str, time_period: int = 1):
        self.name = name
        self.max_output = max_output
        self.time_period = time_period
        self.current_output = 0
        self.private_key = account
        self.account = blockchain_manager.get_account(account)

    def authorize(self):
        try:
            producer_contract = blockchain_manager.contracts['PRODUCER']
            contract_function = producer_contract.functions.addAuthorizedProducer(self.account.address)
            tx_params = blockchain_manager.get_transaction_params(AUTHORIZER_ADDRESS)
            tx_params = contract_function.build_transaction(tx_params)
            receipt = blockchain_manager.send_transaction(tx_params, AUTHORIZER_PRIVATE_KEY)
            
            if receipt:
                logger.info(f"{self.name} authorized as producer. Transaction hash: {receipt['transactionHash'].hex()}")
            else:
                raise Exception(f"Failed to authorize {self.name} as producer")
        except Exception as e:
            logger.error(f"Error in authorizing producer: {e}")
            raise

    @property
    def max_output_for_period(self):
        return round(self.max_output * self.time_period)

    @property
    def available_output(self):
        return max(self.max_output_for_period - self.current_output, 0)

    def reset(self):
        self.current_output = 0
        logger.info(f"{self.name} output reset to 0")

    def request_power(self, requested_output: int):
        provided_power = min(requested_output, self.available_output)
        self.current_output += provided_power
        logger.info(f'Producer {self.name} generated {provided_power} Wh')
        return provided_power