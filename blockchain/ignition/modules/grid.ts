import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

const EnergyGridModule = buildModule("EnergyGridModule", (builder) => {
  const energyToken = builder.contract("EnergyToken");

  const producer = builder.contract("Producer", [energyToken]);
  const transmissionLine = builder.contract("TransmissionLine", [energyToken]);
  const substation = builder.contract("Substation", [energyToken]);
  const consumer = builder.contract("Consumer", [energyToken]);

  // Set up initial configurations
  builder.call(energyToken, "addProducer", [producer]);

  builder.call(producer, "addAuthorizedProducer", [builder.getAccount(0)]);
  builder.call(producer, "connectTransmissionLine", [transmissionLine]);
  builder.call(transmissionLine, "addAuthorizedOperator", [
    builder.getAccount(0),
  ]);

  builder.call(substation, "addAuthorizedOperator", [builder.getAccount(0)]);
  builder.call(substation, "registerConsumer", [consumer]);
  builder.call(consumer, "addAuthorizedManager", [builder.getAccount(0)]);

  return {
    energyToken,
    producer,
    transmissionLine,
    substation,
    consumer,
  };
});

module.exports = EnergyGridModule;
