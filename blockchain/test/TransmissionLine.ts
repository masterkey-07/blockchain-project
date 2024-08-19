import { expect } from "chai";
import { ethers } from "hardhat";
import { Contract, Signer } from "ethers";
import { EnergyToken, TransmissionLine } from "../typechain-types";
import { DeployableTransaction } from "./types";

describe("TransmissionLine", function () {
  let transmissionLine: TransmissionLine & DeployableTransaction;
  let energyToken: EnergyToken & DeployableTransaction;
  let owner: Signer;
  let authorizedOperator: Signer;
  let to: Signer;
  let unauthorizedAccount: Signer;

  beforeEach(async function () {
    [owner, authorizedOperator, to, unauthorizedAccount] =
      await ethers.getSigners();

    const EnergyToken = await ethers.getContractFactory("EnergyToken");
    energyToken = await EnergyToken.deploy();

    const TransmissionLine = await ethers.getContractFactory(
      "TransmissionLine"
    );
    transmissionLine = await TransmissionLine.deploy(
      await energyToken.getAddress()
    );

    await transmissionLine.addAuthorizedOperator(
      await authorizedOperator.getAddress()
    );
    await energyToken.mint(
      await authorizedOperator.getAddress(),
      ethers.parseEther("1000")
    );
    await energyToken
      .connect(authorizedOperator)
      .approve(await transmissionLine.getAddress(), ethers.parseEther("1000"));
  });

  describe("Authorization", function () {
    it("Should add an authorized operator", async function () {
      await transmissionLine.addAuthorizedOperator(
        await unauthorizedAccount.getAddress()
      );
      expect(
        await transmissionLine.authorizedOperators(
          await unauthorizedAccount.getAddress()
        )
      ).to.be.true;
    });

    it("Should remove an authorized operator", async function () {
      await transmissionLine.removeAuthorizedOperator(
        await authorizedOperator.getAddress()
      );
      expect(
        await transmissionLine.authorizedOperators(
          await authorizedOperator.getAddress()
        )
      ).to.be.false;
    });

    it("Should fail when unauthorized account tries to add operator", async function () {
      await expect(
        transmissionLine
          .connect(unauthorizedAccount)
          .addAuthorizedOperator(await unauthorizedAccount.getAddress())
      ).to.be.revertedWith("Not authorized");
    });
  });

  describe("Energy transmission", function () {
    it("Should transmit energy tokens", async function () {
      const amount = ethers.parseEther("10");
      await transmissionLine
        .connect(authorizedOperator)
        .transmitEnergy(await to.getAddress(), amount);
      expect(await energyToken.balanceOf(await to.getAddress())).to.equal(
        amount
      );
    });

    it("Should fail if there are insufficient tokens", async function () {
      const amount = ethers.parseEther("1001");
      await expect(
        transmissionLine
          .connect(authorizedOperator)
          .transmitEnergy(await to.getAddress(), amount)
      ).to.be.revertedWithCustomError(
        { interface: energyToken.interface },
        "ERC20InsufficientAllowance"
      );
    });

    it("Should fail if called by unauthorized account", async function () {
      const amount = ethers.parseEther("10");

      await expect(
        transmissionLine
          .connect(unauthorizedAccount)
          .transmitEnergy(await to.getAddress(), amount)
      ).to.be.revertedWith("Not authorized");
    });
  });
});
