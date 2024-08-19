from .blockchain import get_account, get_transaction_params, send_transaction, producer_contract

class PowerPlant:
    def __init__(self, name:str, max_output:int, account:str, time_period:int=1):
        self.__name = name
        self.__max_output = max_output
        self.__time_period = time_period
        self.__current_output = 0

        self.private = account
        self.__account = get_account(account)

    def authorize(self, authorizer_address, authorizer_private_key):
        try:
            contract_function = producer_contract.functions.addAuthorizedProducer(self.__account.address)

            tx_params = contract_function.build_transaction(get_transaction_params(authorizer_address))

            receipt = send_transaction(tx_params, authorizer_private_key)
            
            if receipt:
                print(f"{self.__name} authorized as producer. Transaction hash: {receipt['transactionHash'].hex()}")
            else:
                raise Exception(f"Failed to authorize {self.__name} as producer")
        except Exception as e:
            print(f"Error in become_authorized_producer: {e}")


    def get_producer_account(self):
        return self.__account

    def get_max_output(self):
        return round(self.__max_output * self.__time_period)

    def get_available_output(self):
        max_output = self.get_max_output()
        
        if max(max_output - self.__current_output, 0) == 0:
            return 0
        
        return max_output - self.__current_output

    def reset(self):
        self.__current_output = 0

    def request_power(self, requested_output:int):
        max_output = self.get_max_output()

        provided_power = min(requested_output, max_output - self.__current_output)

        self.__current_output += provided_power

        print(f'Producer {self.__name} generated {provided_power} Wh')

        return provided_power