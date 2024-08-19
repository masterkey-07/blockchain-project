import { expect } from "chai";
import hardhat from "hardhat";
import { loadFixture } from "@nomicfoundation/hardhat-toolbox/network-helpers";

describe("Producer", function () {
  async function deployProducerFixture() {
    const [owner, firstAddress] = await hardhat.ethers.getSigners();

    const EnergyToken = await hardhat.ethers.getContractFactory("EnergyToken");
    const energyToken = await EnergyToken.deploy();

    const Producer = await hardhat.ethers.getContractFactory("Producer");
    const producer = await Producer.deploy(await energyToken.getAddress());

    return {
      owner,
      producer,
      Producer,
      energyToken,
      EnergyToken,
      firstAddress,
    };
  }

  describe("Deployment", function () {
    it("Should set the correct EnergyToken address", async function () {
      const { producer, energyToken } = await loadFixture(
        deployProducerFixture
      );

      expect(await producer.energyToken()).to.equal(
        await energyToken.getAddress()
      );
    });
  });

  describe("Producing Energy with Multiple Producers", function () {
    it("Should allow multiple producers to mint tokens", async function () {
      const { firstAddress, producer, energyToken, owner } = await loadFixture(
        deployProducerFixture
      );

      // Deploy a second producer
      const Producer = await hardhat.ethers.getContractFactory("Producer");
      const secondProducer = await Producer.deploy(
        await energyToken.getAddress()
      );

      // Add both producers as authorized minters
      await energyToken.connect(owner).addProducer(await producer.getAddress());
      await energyToken
        .connect(owner)
        .addProducer(await secondProducer.getAddress());

      const amount1 = hardhat.ethers.parseUnits("1000", 18);
      const amount2 = hardhat.ethers.parseUnits("500", 18);

      // Both producers mint tokens
      await producer.produceEnergy(firstAddress.address, amount1);
      await secondProducer.produceEnergy(firstAddress.address, amount2);

      const balance = await energyToken.balanceOf(firstAddress.address);

      expect(balance).to.equal(amount1 + amount2);
    });
  });
});
