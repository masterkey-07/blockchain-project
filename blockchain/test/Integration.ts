import { expect } from "chai";
import { ethers } from "hardhat";
import { Contract, Signer } from "ethers";
import { DeployableTransaction } from "./types";
import {
  Consumer,
  EnergyToken,
  Producer,
  Substation,
  TransmissionLine,
} from "../typechain-types";

describe("Energy Network Integration", function () {
  let energyToken: EnergyToken & DeployableTransaction;
  let producer: Producer & DeployableTransaction;
  let transmissionLine: TransmissionLine & DeployableTransaction;
  let substation: Substation & DeployableTransaction;
  let consumer: Consumer & DeployableTransaction;

  let owner: Signer;
  let producerOperator: Signer;
  let transmissionOperator: Signer;
  let substationOperator: Signer;
  let consumerAccount: Signer;

  const INITIAL_SUPPLY = ethers.parseEther("10000");
  const PRODUCTION_AMOUNT = ethers.parseEther("100");
  const TRANSMISSION_AMOUNT = ethers.parseEther("90");
  const DISTRIBUTION_AMOUNT = ethers.parseEther("80");
  const CONSUMPTION_AMOUNT = ethers.parseEther("70");

  beforeEach(async function () {
    [
      owner,
      producerOperator,
      transmissionOperator,
      substationOperator,
      consumerAccount,
    ] = await ethers.getSigners();

    // Deploy EnergyToken
    const EnergyToken = await ethers.getContractFactory("EnergyToken");
    energyToken = await EnergyToken.deploy();

    // Deploy Producer
    const Producer = await ethers.getContractFactory("Producer");
    producer = await Producer.deploy(await energyToken.getAddress());

    // Deploy TransmissionLine
    const TransmissionLine = await ethers.getContractFactory(
      "TransmissionLine"
    );
    transmissionLine = await TransmissionLine.deploy(
      await energyToken.getAddress()
    );

    // Deploy Substation
    const Substation = await ethers.getContractFactory("Substation");
    substation = await Substation.deploy(await energyToken.getAddress());

    // Deploy Consumer
    const Consumer = await ethers.getContractFactory("Consumer");
    consumer = await Consumer.deploy(await energyToken.getAddress());

    // Setup
    await energyToken.addProducer(await producer.getAddress());

    await producer.addAuthorizedProducer(await producerOperator.getAddress());

    await producer.connectTransmissionLine(
      await transmissionOperator.getAddress()
    );

    await transmissionLine.addAuthorizedOperator(
      await transmissionOperator.getAddress()
    );

    await consumer.addAuthorizedManager(await consumerAccount.getAddress());

    await substation.addAuthorizedOperator(
      await substationOperator.getAddress()
    );

    await substation
      .connect(substationOperator)
      .registerConsumer(await consumerAccount.getAddress());

    // Approve token transfers
    await energyToken
      .connect(transmissionOperator)
      .approve(await substation.getAddress(), INITIAL_SUPPLY);

    // Approve token transfers
    await energyToken
      .connect(transmissionOperator)
      .approve(await transmissionLine.getAddress(), INITIAL_SUPPLY);

    await energyToken
      .connect(consumerAccount)
      .approve(await consumer.getAddress(), INITIAL_SUPPLY);

    await energyToken
      .connect(substationOperator)
      .approve(await substation.getAddress(), INITIAL_SUPPLY);
  });

  it("Should simulate the entire energy flow", async function () {
    // 1. Produce energy
    await producer
      .connect(producerOperator)
      .produceEnergy(
        await transmissionOperator.getAddress(),
        PRODUCTION_AMOUNT
      );

    expect(
      await energyToken.balanceOf(await transmissionOperator.getAddress())
    ).to.equal(PRODUCTION_AMOUNT);

    // 2. Transmit energy
    await transmissionLine
      .connect(transmissionOperator)
      .transmitEnergy(
        await substationOperator.getAddress(),
        TRANSMISSION_AMOUNT
      );

    expect(
      await energyToken.balanceOf(await substationOperator.getAddress())
    ).to.equal(TRANSMISSION_AMOUNT);

    expect(
      await energyToken.balanceOf(await transmissionOperator.getAddress())
    ).to.equal(PRODUCTION_AMOUNT - TRANSMISSION_AMOUNT);

    // 3. Distribute energy
    await substation
      .connect(substationOperator)
      .distributeEnergy(
        await consumerAccount.getAddress(),
        DISTRIBUTION_AMOUNT
      );

    expect(
      await energyToken.balanceOf(await consumerAccount.getAddress())
    ).to.equal(DISTRIBUTION_AMOUNT);

    expect(
      await energyToken.balanceOf(await substationOperator.getAddress())
    ).to.equal(TRANSMISSION_AMOUNT - DISTRIBUTION_AMOUNT);

    // 4. Consume energy
    await consumer.connect(consumerAccount).consumeEnergy(CONSUMPTION_AMOUNT);

    expect(
      await energyToken.balanceOf(await consumerAccount.getAddress())
    ).to.equal(DISTRIBUTION_AMOUNT - CONSUMPTION_AMOUNT);

    // 5. Verify final balances
    expect(
      await energyToken.balanceOf(await transmissionOperator.getAddress())
    ).to.equal(PRODUCTION_AMOUNT - TRANSMISSION_AMOUNT);

    expect(
      await energyToken.balanceOf(await substationOperator.getAddress())
    ).to.equal(TRANSMISSION_AMOUNT - DISTRIBUTION_AMOUNT);

    expect(
      await energyToken.balanceOf(await consumerAccount.getAddress())
    ).to.equal(DISTRIBUTION_AMOUNT - CONSUMPTION_AMOUNT);
  });
});
