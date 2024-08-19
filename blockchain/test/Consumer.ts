import { expect } from "chai";
import { ethers } from "hardhat";
import { Contract, Signer } from "ethers";
import { DeployableTransaction } from "./types";
import { Consumer, EnergyToken } from "../typechain-types";

describe("Consumer", function () {
  let consumer: Consumer & DeployableTransaction;
  let energyToken: EnergyToken & DeployableTransaction;
  let owner: Signer;
  let authorizedManager: Signer;
  let unauthorizedAccount: Signer;

  beforeEach(async function () {
    [owner, authorizedManager, unauthorizedAccount] = await ethers.getSigners();

    const EnergyToken = await ethers.getContractFactory("EnergyToken");
    energyToken = await EnergyToken.deploy();

    const Consumer = await ethers.getContractFactory("Consumer");
    consumer = await Consumer.deploy(await energyToken.getAddress());

    await consumer.addAuthorizedManager(await authorizedManager.getAddress());

    await energyToken.mint(
      await authorizedManager.getAddress(),
      ethers.parseEther("1000")
    );

    await energyToken
      .connect(authorizedManager)
      .approve(await consumer.getAddress(), ethers.parseEther("1000"));
  });

  describe("Authorization", function () {
    it("Should add an authorized manager", async function () {
      await consumer.addAuthorizedManager(
        await unauthorizedAccount.getAddress()
      );
      expect(
        await consumer.authorizedManagers(
          await unauthorizedAccount.getAddress()
        )
      ).to.be.true;
    });

    it("Should remove an authorized manager", async function () {
      await consumer.removeAuthorizedManager(
        await authorizedManager.getAddress()
      );
      expect(
        await consumer.authorizedManagers(await authorizedManager.getAddress())
      ).to.be.false;
    });

    it("Should fail when unauthorized account tries to add manager", async function () {
      await expect(
        consumer
          .connect(unauthorizedAccount)
          .addAuthorizedManager(await unauthorizedAccount.getAddress())
      ).to.be.revertedWith("Not authorized");
    });
  });

  describe("Energy consumption", function () {
    it("Should consume energy tokens", async function () {
      const amount = ethers.parseEther("10");

      await consumer.connect(authorizedManager).consumeEnergy(amount);

      expect(
        await energyToken.balanceOf(await authorizedManager.getAddress())
      ).to.equal(ethers.parseEther("990"));
    });

    it("Should fail if unauthorized account is not approved", async function () {
      const amount = ethers.parseEther("10");

      await expect(
        consumer.connect(unauthorizedAccount).consumeEnergy(amount)
      ).to.be.revertedWith("Not authorized");
    });

    it("Should fail if there are insufficient tokens", async function () {
      const amount = ethers.parseEther("1001");

      await expect(
        consumer.connect(authorizedManager).consumeEnergy(amount)
      ).to.be.revertedWith("Insufficient energy tokens");
    });
  });
});
