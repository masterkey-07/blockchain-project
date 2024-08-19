import math
from .consumer import Consumer
from .power_plant import PowerPlant
from .transmission_line import TransmissionLine
from .blockchain import *

type producer_line = tuple[PowerPlant, TransmissionLine]

class Substation:
    def __init__(self, name:str, account):
        self.__name = name
        self.__connected_producers:list[producer_line] = []
        self.__connected_consumers:list[Consumer] = []
        self.__account = get_account(account)
        self.private = account

    def get_account(self):
        return self.__account

    def authorize(self, authorizer_address, authorizer_private_key):
        try:
            contract_function = substation_contract.functions.addAuthorizedOperator(self.__account.address)

            tx_params = contract_function.build_transaction(get_transaction_params(authorizer_address))

            receipt = send_transaction(tx_params, authorizer_private_key)
            
            if receipt:
                print(f"{self.__name} authorized as a substation. Transaction hash: {receipt['transactionHash'].hex()}")
            else:
                print(f"Failed to authorize {self.__name} as a substation")
        except Exception as e:
            print(f"Error in become authorized: {e}")
        finally:
            try:
                tx = energy_token_contract.functions.approve(substation_contract.address, 1_000_000_000_000_000).build_transaction(
                    get_transaction_params(self.get_account().address)
                )
                receipt = send_transaction(tx, self.private)
                if receipt:
                    print(f"Token transfer approved. Transaction hash: {receipt['transactionHash'].hex()}")
                else:
                    print("Failed to approve token transfer")
            except Exception as e:
                raise Exception(f"Error in approve_token_transfer: {e}")


    def connect_producer(self, producer:PowerPlant, transmission_line:TransmissionLine):
        tx = producer_contract.functions.connectTransmissionLine(transmission_line.get_account().address).build_transaction(
            get_transaction_params(producer.get_producer_account().address)
        )
        receipt = send_transaction(tx, producer.private)

        if receipt:
            print(f"Transmission line connected. Transaction hash: {receipt['transactionHash'].hex()}")
        else:
            raise Exception("Failed to connect transmission line")    
        
        self.__connected_producers.append((producer, transmission_line))

    def connect_consumer(self, consumer:Consumer):
        contract_function = substation_contract.functions.registerConsumer(consumer.get_account().address)

        tx_params = contract_function.build_transaction(get_transaction_params(AUTHORIZER_ADDRESS))

        receipt = send_transaction(tx_params, AUTHORIZER_PRIVATE_KEY)
        
        if receipt:
            print(f"{self.__name} authorized as a consumer. Transaction hash: {receipt['transactionHash'].hex()}")
        else:
            raise Exception(f"Failed to authorize {self.__name} as a consumer")

        
        consumer.connect_to_substation(self)

        self.__connected_consumers.append(consumer)

    def reset(self):
        for producer in self.__connected_producers:
            producer[0].reset()

        for consumer in self.__connected_consumers:
            consumer.reset()

    def distribute_power(self):
        print(f"Substation {self.__name} started the distribution")

        available_capacity = sum(producer.get_available_output() for producer, _ in self.__connected_producers)
        
        if available_capacity == 0:
            raise Exception("There is no Power Capacity!")

        total_demand = sum(consumer.get_demand() for consumer in self.__connected_consumers)

        if total_demand == 0:
            raise Exception("There is no Demand!")
        
        total_power = 0

        for producer, line in self.__connected_producers:
            proportional_request = (producer.get_available_output() / available_capacity) * total_demand

            generated_power = producer.request_power(proportional_request)            

            tx = producer_contract.functions.produceEnergy(line.get_account().address, round(generated_power)).build_transaction(
                get_transaction_params(producer.get_producer_account().address)
            )

            receipt = send_transaction(tx, producer.private)

            if receipt:
                print(f"Power generated. Transaction hash: {receipt['transactionHash'].hex()}")
            else:
                raise Exception("Failed to connect transmission line")    

            transmitted_power = line.transmit(generated_power)

            tx = transmission_line_contract.functions.transmitEnergy(self.__account.address, round(transmitted_power)).build_transaction(
                get_transaction_params(line.get_account().address)
            )

            receipt = send_transaction(tx, line.private)

            if receipt:
                print(f"Power generated. Transaction hash: {receipt['transactionHash'].hex()}")
            else:
                raise Exception("Failed to connect transmission line")    


            total_power += transmitted_power

        for consumer in self.__connected_consumers:
            proportion = consumer.get_demand() / total_demand
            
            energy_distributed = math.floor(total_power * proportion)

            tx = substation_contract.functions.distributeEnergy(consumer.get_account().address, round(energy_distributed)).build_transaction(
                get_transaction_params(self.get_account().address)
            )

            receipt = send_transaction(tx, self.private)

            if receipt:
                print(f"Power generated. Transaction hash: {receipt['transactionHash'].hex()}")
            else:
                raise Exception("Failed to connect transmission line")    

            tx = consumer_contract.functions.consumeEnergy(round(energy_distributed)).build_transaction(
                get_transaction_params(consumer.get_account().address)
            )

            receipt = send_transaction(tx, consumer.private)

            if receipt:
                print(f"Power generated. Transaction hash: {receipt['transactionHash'].hex()}")
            else:
                raise Exception("Failed to connect transmission line")    

            consumer.consume_power(energy_distributed)



