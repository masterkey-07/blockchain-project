from .blockchain import *

class TransmissionLine:
    def __init__(self, name:str, account):
        self.__name = name
        self.__account = get_account(account)
        self.private = account

    def get_account(self):
        return self.__account

    def authorize(self, authorizer_address, authorizer_private_key):
        try:
            contract_function = transmission_line_contract.functions.addAuthorizedOperator(self.__account.address)

            tx_params = contract_function.build_transaction(get_transaction_params(authorizer_address))

            receipt = send_transaction(tx_params, authorizer_private_key)
            
            if receipt:
                print(f"{self.__name} authorized as a transmission line. Transaction hash: {receipt['transactionHash'].hex()}")
            else:
                raise Exception(f"Failed to authorize {self.__name} as a transmission line")
        except Exception as e:
            raise Exception(f"Error in become authorized: {e}")
        finally:
            
            try:
                tx = energy_token_contract.functions.approve(transmission_line_contract.address, 1_000_000_000_000_000).build_transaction(
                    get_transaction_params(self.get_account().address)
                )
                receipt = send_transaction(tx, self.private)
                if receipt:
                    print(f"Token transfer approved. Transaction hash: {receipt['transactionHash'].hex()}")
                else:
                    print("Failed to approve token transfer")
            except Exception as e:
                raise Exception(f"Error in approve_token_transfer: {e}")



    def transmit(self, transmitted_power:int):        
        print(f"{self.__name} transmitted {transmitted_power} Wh")
        
        return transmitted_power

