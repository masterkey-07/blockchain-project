import math
import logging
from .consumer import Consumer
from .power_plant import PowerPlant
from .transmission_line import TransmissionLine
from .blockchain import blockchain_manager, AUTHORIZER_ADDRESS, AUTHORIZER_PRIVATE_KEY

logger = logging.getLogger(__name__)

class Substation:
    def __init__(self, name: str, account: str):
        self.name = name
        self.connected_producers = []
        self.connected_consumers = []
        self.account = blockchain_manager.get_account(account)
        self.private_key = account

    def authorize(self):
        try:
            substation_contract = blockchain_manager.contracts['SUBSTATION']
            contract_function = substation_contract.functions.addAuthorizedOperator(self.account.address)
            tx_params = blockchain_manager.get_transaction_params(AUTHORIZER_ADDRESS)
            tx_params = contract_function.build_transaction(tx_params)
            receipt = blockchain_manager.send_transaction(tx_params, AUTHORIZER_PRIVATE_KEY)
            
            if receipt:
                logger.info(f"{self.name} authorized as a substation. Transaction hash: {receipt['transactionHash'].hex()}")
                self._approve_token_transfer()
            else:
                raise Exception(f"Failed to authorize {self.name} as a substation")
        except Exception as e:
            logger.error(f"Error in authorizing substation: {e}")
            raise

    def _approve_token_transfer(self):
        try:
            energy_token_contract = blockchain_manager.contracts['ENERGY_TOKEN']
            substation_contract = blockchain_manager.contracts['SUBSTATION']
            tx = energy_token_contract.functions.approve(substation_contract.address, 1_000_000_000_000_000).build_transaction(
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

    def connect_producer(self, producer: PowerPlant, transmission_line: TransmissionLine):
        try:
            producer_contract = blockchain_manager.contracts['PRODUCER']
            tx = producer_contract.functions.connectTransmissionLine(transmission_line.account.address).build_transaction(
                blockchain_manager.get_transaction_params(producer.account.address)
            )
            receipt = blockchain_manager.send_transaction(tx, producer.private_key)

            if receipt:
                logger.info(f"Transmission line connected to producer {producer.name}. Transaction hash: {receipt['transactionHash'].hex()}")
                self.connected_producers.append((producer, transmission_line))
            else:
                raise Exception("Failed to connect transmission line")
        except Exception as e:
            logger.error(f"Error connecting producer to transmission line: {e}")
            raise

    def connect_consumer(self, consumer: Consumer):
        try:
            substation_contract = blockchain_manager.contracts['SUBSTATION']
            contract_function = substation_contract.functions.registerConsumer(consumer.account.address)
            tx_params = blockchain_manager.get_transaction_params(AUTHORIZER_ADDRESS)
            tx_params = contract_function.build_transaction(tx_params)
            receipt = blockchain_manager.send_transaction(tx_params, AUTHORIZER_PRIVATE_KEY)
            
            if receipt:
                logger.info(f"Consumer {consumer.name} registered with {self.name}. Transaction hash: {receipt['transactionHash'].hex()}")
                consumer.connect_to_substation(self)
                self.connected_consumers.append(consumer)
            else:
                raise Exception(f"Failed to register consumer {consumer.name}")
        except Exception as e:
            logger.error(f"Error connecting consumer to substation: {e}")
            raise

    def reset(self):
        for producer, _ in self.connected_producers:
            producer.reset()
        for consumer in self.connected_consumers:
            consumer.reset()
        logger.info(f"Substation {self.name} reset all connected producers and consumers")

    def distribute_power(self):
        logger.info(f"Substation {self.name} started power distribution")

        available_capacity = sum(producer.available_output for producer, _ in self.connected_producers)
        if available_capacity == 0:
            logger.warning("No power capacity available!")
            return

        total_demand = sum(consumer.get_demand() for consumer in self.connected_consumers)
        if total_demand == 0:
            logger.warning("No power demand!")
            return
        
        total_power = self._generate_and_transmit_power(available_capacity, total_demand)
        self._distribute_to_consumers(total_power, total_demand)

    def _generate_and_transmit_power(self, available_capacity, total_demand):
        total_power = 0
        for producer, line in self.connected_producers:
            proportional_request = (producer.available_output / available_capacity) * total_demand
            generated_power = producer.request_power(proportional_request)
            self._record_power_generation(producer, line, generated_power)
            transmitted_power = line.transmit(generated_power)
            self._record_power_transmission(line, transmitted_power)
            total_power += transmitted_power
        return total_power

    def _record_power_generation(self, producer: PowerPlant, line: TransmissionLine, generated_power: int):
        try:
            producer_contract = blockchain_manager.contracts['PRODUCER']
            tx = producer_contract.functions.produceEnergy(line.account.address, round(generated_power)).build_transaction(
                blockchain_manager.get_transaction_params(producer.account.address)
            )
            receipt = blockchain_manager.send_transaction(tx, producer.private_key)
            if receipt:
                logger.info(f"Power generation recorded for {producer.name}. Amount: {generated_power} Wh. Transaction hash: {receipt['transactionHash'].hex()}")
            else:
                raise Exception("Failed to record power generation")
        except Exception as e:
            logger.error(f"Error in recording power generation: {e}")
            raise

    def _record_power_transmission(self, line: TransmissionLine, transmitted_power: int):
        try:
            transmission_line_contract = blockchain_manager.contracts['TRANSMISSION_LINE']
            tx = transmission_line_contract.functions.transmitEnergy(self.account.address, round(transmitted_power)).build_transaction(
                blockchain_manager.get_transaction_params(line.account.address)
            )
            receipt = blockchain_manager.send_transaction(tx, line.private_key)
            if receipt:
                logger.info(f"Power transmission recorded for {line.name}. Amount: {transmitted_power} Wh. Transaction hash: {receipt['transactionHash'].hex()}")
            else:
                raise Exception("Failed to record power transmission")
        except Exception as e:
            logger.error(f"Error in recording power transmission: {e}")
            raise

    def _distribute_to_consumers(self, total_power: float, total_demand: float):
        for consumer in self.connected_consumers:
            proportion = consumer.get_demand() / total_demand
            energy_distributed = math.floor(total_power * proportion)
            self._record_energy_distribution(consumer, energy_distributed)
            self._record_energy_consumption(consumer, energy_distributed)
            consumer.consume_power(energy_distributed)

    def _record_energy_distribution(self, consumer: Consumer, energy_distributed: int):
        try:
            substation_contract = blockchain_manager.contracts['SUBSTATION']
            tx = substation_contract.functions.distributeEnergy(consumer.account.address, round(energy_distributed)).build_transaction(
                blockchain_manager.get_transaction_params(self.account.address)
            )
            receipt = blockchain_manager.send_transaction(tx, self.private_key)
            if receipt:
                logger.info(f"Energy distribution recorded for {consumer.name}. Amount: {energy_distributed} Wh. Transaction hash: {receipt['transactionHash'].hex()}")
            else:
                raise Exception("Failed to record energy distribution")
        except Exception as e:
            logger.error(f"Error in recording energy distribution: {e}")
            raise

    def _record_energy_consumption(self, consumer: Consumer, energy_consumed: int):
        try:
            consumer_contract = blockchain_manager.contracts['CONSUMER']
            tx = consumer_contract.functions.consumeEnergy(round(energy_consumed)).build_transaction(
                blockchain_manager.get_transaction_params(consumer.account.address)
            )
            receipt = blockchain_manager.send_transaction(tx, consumer.private_key)
            if receipt:
                logger.info(f"Energy consumption recorded for {consumer.name}. Amount: {energy_consumed} Wh. Transaction hash: {receipt['transactionHash'].hex()}")
            else:
                raise Exception("Failed to record energy consumption")
        except Exception as e:
            logger.error(f"Error in recording energy consumption: {e}")
            raise