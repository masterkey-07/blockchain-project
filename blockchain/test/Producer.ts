import { expect } from "chai";
import { ethers } from "hardhat";
import { Contract, Signer } from "ethers";
import { DeployableTransaction } from "./types";
import { EnergyToken, Producer } from "../typechain-types";

describe("Producer", function () {
  let producer: Producer & DeployableTransaction;
  let energyToken: EnergyToken & DeployableTransaction;
  let owner: Signer;
  let authorizedProducer: Signer;
  let transmissionLine: Signer;
  let unauthorizedAccount: Signer;

  beforeEach(async function () {
    [owner, authorizedProducer, transmissionLine, unauthorizedAccount] =
      await ethers.getSigners();

    const EnergyToken = await ethers.getContractFactory("EnergyToken");
    energyToken = await EnergyToken.deploy();

    const Producer = await ethers.getContractFactory("Producer");
    producer = await Producer.deploy(await energyToken.getAddress());

    await producer.addAuthorizedProducer(await authorizedProducer.getAddress());
    await energyToken.addProducer(await producer.getAddress());
  });

  describe("Authorization", function () {
    it("Should add an authorized producer", async function () {
      await producer.addAuthorizedProducer(
        await unauthorizedAccount.getAddress()
      );
      expect(
        await producer.authorizedProducers(
          await unauthorizedAccount.getAddress()
        )
      ).to.be.true;
    });

    it("Should remove an authorized producer", async function () {
      await producer.removeAuthorizedProducer(
        await authorizedProducer.getAddress()
      );
      expect(
        await producer.authorizedProducers(
          await authorizedProducer.getAddress()
        )
      ).to.be.false;
    });

    it("Should fail when unauthorized account tries to add producer", async function () {
      await expect(
        producer
          .connect(unauthorizedAccount)
          .addAuthorizedProducer(await unauthorizedAccount.getAddress())
      ).to.be.revertedWith("Not authorized");
    });
  });

  describe("Transmission line connection", function () {
    it("Should connect a transmission line", async function () {
      await producer.connectTransmissionLine(
        await transmissionLine.getAddress()
      );
      expect(
        await producer.connectedTransmissionLines(
          await transmissionLine.getAddress()
        )
      ).to.be.true;
    });

    it("Should disconnect a transmission line", async function () {
      await producer.connectTransmissionLine(
        await transmissionLine.getAddress()
      );
      await producer.disconnectTransmissionLine(
        await transmissionLine.getAddress()
      );
      expect(
        await producer.connectedTransmissionLines(
          await transmissionLine.getAddress()
        )
      ).to.be.false;
    });
  });

  describe("Energy production", function () {
    it("Should produce energy tokens", async function () {
      await producer.connectTransmissionLine(
        await transmissionLine.getAddress()
      );
      const amount = ethers.parseEther("10");
      await producer
        .connect(authorizedProducer)
        .produceEnergy(await transmissionLine.getAddress(), amount);
      expect(
        await energyToken.balanceOf(await transmissionLine.getAddress())
      ).to.equal(amount);
    });

    it("Should fail if transmission line is not connected", async function () {
      const amount = ethers.parseEther("10");
      await expect(
        producer
          .connect(authorizedProducer)
          .produceEnergy(await transmissionLine.getAddress(), amount)
      ).to.be.revertedWith("TransmissionLine not connected");
    });

    it("Should fail if called by unauthorized account", async function () {
      await producer.connectTransmissionLine(
        await transmissionLine.getAddress()
      );
      const amount = ethers.parseEther("10");
      await expect(
        producer
          .connect(unauthorizedAccount)
          .produceEnergy(await transmissionLine.getAddress(), amount)
      ).to.be.revertedWith("Not authorized");
    });
  });
});
