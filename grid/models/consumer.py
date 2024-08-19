import random
from .blockchain import *

class Consumer:
    def __init__(self, name: str, min_demand: float, max_demand: float, account:str, time_period: int = 1):
        self.__name = name
        self.__substations:set = set()
        self.__min_demand = min_demand
        self.__max_demand = max_demand
        self.__time_period = time_period
        
        self.private = account
        self.__current_demand:int = None
        self.__account = get_account(account)

    def get_account(self):
        return self.__account

    def authorize(self, authorizer_address, authorizer_private_key):
        try:
            contract_function = consumer_contract.functions.addAuthorizedManager(self.__account.address)

            tx_params = contract_function.build_transaction(get_transaction_params(authorizer_address))

            receipt = send_transaction(tx_params, authorizer_private_key)
            
            if receipt:
                print(f"{self.__name} authorized as consumer. Transaction hash: {receipt['transactionHash'].hex()}")
            else:
                raise Exception(f"Failed to authorize {self.__name} as consumer")
        except Exception as e:
            print(f"Error in become_authorized_consumer: {e}")
        finally:
            try:
                tx = energy_token_contract.functions.approve(consumer_contract.address, 1_000_000_000_000_000).build_transaction(
                    get_transaction_params(self.get_account().address)
                )
                receipt = send_transaction(tx, self.private)
                if receipt:
                    print(f"Token transfer approved. Transaction hash: {receipt['transactionHash'].hex()}")
                else:
                    print("Failed to approve token transfer")
            except Exception as e:
                raise Exception(f"Error in approve_token_transfer: {e}")


    def reset(self):
        self.__current_demand = None

    def connect_to_substation(self, substation):
        self.__substations.add(substation)

    def get_quantity_of_substations(self):
        return len(self.__substations)

    def __get_new_demand(self):
        random_demand = random.uniform(self.__min_demand, self.__max_demand)

        return round(random_demand * self.__time_period)
    
    def get_demand(self) -> float:
        if (self.__current_demand is None):
            self.__current_demand = self.__get_new_demand()
            return self.__current_demand
        
        return self.__current_demand / len(self.__substations)
        
    def consume_power(self, received: int):
        print(f"{self.__name} received {received} of {self.get_demand()} Wh")
