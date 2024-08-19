import { expect } from "chai";
import { ethers } from "hardhat";
import { Contract, Signer } from "ethers";

describe("TransmissionLine", function () {
  let energyToken: Contract;
  let transmissionLine: Contract;
  let owner: Signer;
  let producer: Signer;
  let substation: Signer;
  let otherAccount: Signer;

  const INITIAL_SUPPLY = ethers.parseEther("1000000");
  const TRANSMISSION_AMOUNT = ethers.parseEther("1000");

  beforeEach(async function () {
    [owner, producer, substation, otherAccount] = await ethers.getSigners();

    const EnergyToken = await ethers.getContractFactory("EnergyToken");
    energyToken = await EnergyToken.deploy();

    const TransmissionLine = await ethers.getContractFactory(
      "TransmissionLine"
    );
    transmissionLine = await TransmissionLine.deploy(
      await energyToken.getAddress(),
      await substation.getAddress()
    );

    // Mint some tokens to the producer
    await energyToken
      .connect(owner)
      .mint(await producer.getAddress(), INITIAL_SUPPLY);

    // Approve TransmissionLine to spend producer's tokens
    await energyToken
      .connect(producer)
      .approve(await transmissionLine.getAddress(), INITIAL_SUPPLY);
  });

  describe("Deployment", function () {
    it("Should set the correct EnergyToken address", async function () {
      expect(await transmissionLine.energyToken()).to.equal(
        await energyToken.getAddress()
      );
    });

    it("Should set the correct substation address", async function () {
      expect(await transmissionLine.substation()).to.equal(
        await substation.getAddress()
      );
    });
  });

  describe("Transmit Energy", function () {
    it("Should transmit energy with correct loss", async function () {
      await transmissionLine
        .connect(producer)
        .transmitEnergy(TRANSMISSION_AMOUNT);

      const expectedLoss = (TRANSMISSION_AMOUNT * BigInt(5)) / BigInt(100);
      const expectedTransmitted = TRANSMISSION_AMOUNT - expectedLoss;

      expect(
        await energyToken.balanceOf(await substation.getAddress())
      ).to.equal(expectedTransmitted);
      expect(
        await energyToken.balanceOf(await transmissionLine.getAddress())
      ).to.equal(0);
    });

    it("Should fail if sender doesn't have enough tokens", async function () {
      await expect(
        transmissionLine
          .connect(otherAccount)
          .transmitEnergy(TRANSMISSION_AMOUNT)
      ).to.be.revertedWith("ERC20: insufficient allowance");
    });

    it("Should fail if TransmissionLine is not approved to spend tokens", async function () {
      await energyToken
        .connect(producer)
        .approve(await transmissionLine.getAddress(), 0);
      await expect(
        transmissionLine.connect(producer).transmitEnergy(TRANSMISSION_AMOUNT)
      ).to.be.revertedWith("ERC20: insufficient allowance");
    });

    it("Should emit correct Transfer events", async function () {
      const expectedLoss = (TRANSMISSION_AMOUNT * BigInt(5)) / BigInt(100);
      const expectedTransmitted = TRANSMISSION_AMOUNT - expectedLoss;

      await expect(
        transmissionLine.connect(producer).transmitEnergy(TRANSMISSION_AMOUNT)
      )
        .to.emit(energyToken, "Transfer")
        .withArgs(
          await producer.getAddress(),
          await transmissionLine.getAddress(),
          TRANSMISSION_AMOUNT
        )
        .and.to.emit(energyToken, "Transfer")
        .withArgs(
          await transmissionLine.getAddress(),
          ethers.ZeroAddress,
          expectedLoss
        )
        .and.to.emit(energyToken, "Transfer")
        .withArgs(
          await transmissionLine.getAddress(),
          await substation.getAddress(),
          expectedTransmitted
        );
    });
  });
});
