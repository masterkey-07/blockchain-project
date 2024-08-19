import { expect } from "chai";
import { ethers } from "hardhat";
import { Contract, Signer } from "ethers";
import { EnergyToken, Substation } from "../typechain-types";
import { DeployableTransaction } from "./types";

describe("Substation", function () {
  let substation: Substation & DeployableTransaction;
  let energyToken: EnergyToken & DeployableTransaction;
  let owner: Signer;
  let authorizedOperator: Signer;
  let consumer: Signer;
  let unauthorizedAccount: Signer;

  beforeEach(async function () {
    [owner, authorizedOperator, consumer, unauthorizedAccount] =
      await ethers.getSigners();

    const EnergyToken = await ethers.getContractFactory("EnergyToken");
    energyToken = await EnergyToken.deploy();

    const Substation = await ethers.getContractFactory("Substation");
    substation = await Substation.deploy(await energyToken.getAddress());

    const authorizedOperatorAddress = await authorizedOperator.getAddress();

    await substation.addAuthorizedOperator(authorizedOperatorAddress);

    await energyToken.mint(
      authorizedOperatorAddress,
      ethers.parseEther("1000")
    );

    await energyToken
      .connect(authorizedOperator)
      .approve(await substation.getAddress(), ethers.parseEther("1000"));
  });

  describe("Authorization", function () {
    it("Should add and remove an authorized operator", async function () {
      await substation.addAuthorizedOperator(
        await unauthorizedAccount.getAddress()
      );

      expect(
        await substation.authorizedOperators(
          await unauthorizedAccount.getAddress()
        )
      ).to.be.true;

      await substation.removeAuthorizedOperator(
        await authorizedOperator.getAddress()
      );

      expect(
        await substation.authorizedOperators(
          await authorizedOperator.getAddress()
        )
      ).to.be.false;
    });

    it("Should fail when unauthorized account tries to add operator", async function () {
      await expect(
        substation
          .connect(unauthorizedAccount)
          .addAuthorizedOperator(await unauthorizedAccount.getAddress())
      ).to.be.revertedWith("Not authorized");
    });
  });

  describe("Consumer registration", function () {
    it("Should register and unregister a consumer", async function () {
      const consumerAddress = await consumer.getAddress();

      await substation
        .connect(authorizedOperator)
        .registerConsumer(consumerAddress);

      expect(await substation.registeredConsumers(consumerAddress)).to.be.true;

      await substation
        .connect(authorizedOperator)
        .registerConsumer(consumerAddress);

      await substation
        .connect(authorizedOperator)
        .unregisterConsumer(consumerAddress);

      expect(await substation.registeredConsumers(consumerAddress)).to.be.false;
    });
  });

  describe("Energy distribution", function () {
    it("Should distribute energy tokens", async function () {
      const consumerAddress = await consumer.getAddress();

      await substation
        .connect(authorizedOperator)
        .registerConsumer(consumerAddress);

      const amount = ethers.parseEther("10");

      await substation
        .connect(authorizedOperator)
        .distributeEnergy(consumerAddress, amount);

      expect(await energyToken.balanceOf(consumerAddress)).to.equal(amount);
    });

    it("Should fail if consumer is not registered", async function () {
      const amount = ethers.parseEther("10");
      await expect(
        substation
          .connect(authorizedOperator)
          .distributeEnergy(await consumer.getAddress(), amount)
      ).to.be.revertedWith("Consumer not registered");
    });

    it("Should fail if there are insufficient tokens", async function () {
      await substation
        .connect(authorizedOperator)
        .registerConsumer(await consumer.getAddress());

      const amount = ethers.parseEther("1001");

      await expect(
        substation
          .connect(authorizedOperator)
          .distributeEnergy(await consumer.getAddress(), amount)
      ).to.be.revertedWithCustomError(
        { interface: energyToken.interface },
        "ERC20InsufficientAllowance"
      );
    });
  });
});
