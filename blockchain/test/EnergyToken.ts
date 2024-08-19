import hardhat from "hardhat";
import { expect } from "chai";
import { loadFixture } from "@nomicfoundation/hardhat-toolbox/network-helpers";

describe("EnergyToken", function () {
  async function deployEnergyTokenFixture() {
    const [owner, firstAddress, secondAddress] =
      await hardhat.ethers.getSigners();

    const EnergyToken = await hardhat.ethers.getContractFactory("EnergyToken");
    const energyToken = await EnergyToken.deploy();

    return { EnergyToken, energyToken, owner, firstAddress, secondAddress };
  }

  describe("Deployment", function () {
    it("Should set the correct name and symbol", async function () {
      const { energyToken } = await loadFixture(deployEnergyTokenFixture);

      expect(await energyToken.name()).to.equal("EnergyToken");
      expect(await energyToken.symbol()).to.equal("ENG");
    });

    it("Should assign the total supply of tokens to the owner", async function () {
      const { energyToken, owner } = await loadFixture(
        deployEnergyTokenFixture
      );

      const ownerBalance = await energyToken.balanceOf(
        await owner.getAddress()
      );
      expect(await energyToken.totalSupply()).to.equal(ownerBalance);
    });
  });

  describe("Minting", function () {
    it("Should mint tokens correctly", async function () {
      const { energyToken, firstAddress } = await loadFixture(
        deployEnergyTokenFixture
      );

      await energyToken.mint(await firstAddress.getAddress(), 1000);

      const firstAddressBalance = await energyToken.balanceOf(
        await firstAddress.getAddress()
      );

      expect(firstAddressBalance).to.equal(1000);
    });

    it("Should break if it is not the owner to mint tokens", async function () {
      const { energyToken, firstAddress, secondAddress } = await loadFixture(
        deployEnergyTokenFixture
      );

      await expect(
        energyToken
          .connect(firstAddress)
          .mint(await secondAddress.getAddress(), 1000)
      ).to.be.revertedWith(
        "Only authorized producers or owner can mint tokens"
      );
    });

    it("Should only allow the owner to mint tokens", async function () {
      const { energyToken, owner, firstAddress, secondAddress } =
        await loadFixture(deployEnergyTokenFixture);

      await energyToken
        .connect(owner)
        .mint(await firstAddress.getAddress(), 1000);

      const firstAddressBalance = await energyToken.balanceOf(
        await firstAddress.getAddress()
      );

      expect(firstAddressBalance).to.equal(1000);
    });
  });

  describe("Producer Management", function () {
    it("Should allow owner to add a producer", async function () {
      const { energyToken, firstAddress, owner } = await loadFixture(
        deployEnergyTokenFixture
      );

      await energyToken
        .connect(owner)
        .addProducer(await firstAddress.getAddress());
      expect(
        await energyToken.authorizedProducers(await firstAddress.getAddress())
      ).to.be.true;
    });

    it("Should allow owner to remove a producer", async function () {
      const { energyToken, firstAddress, owner } = await loadFixture(
        deployEnergyTokenFixture
      );
      await energyToken
        .connect(owner)
        .addProducer(await firstAddress.getAddress());
      await energyToken
        .connect(owner)
        .removeProducer(await firstAddress.getAddress());
      expect(
        await energyToken.authorizedProducers(await firstAddress.getAddress())
      ).to.be.false;
    });

    it("Should not allow non-owner to add a producer", async function () {
      const { energyToken, firstAddress, secondAddress } = await loadFixture(
        deployEnergyTokenFixture
      );
      await expect(
        energyToken
          .connect(firstAddress)
          .addProducer(await secondAddress.getAddress())
      ).to.be.revertedWithCustomError(
        energyToken,
        "OwnableUnauthorizedAccount"
      );
    });

    it("Should not allow non-owner to remove a producer", async function () {
      const { energyToken, firstAddress, owner, secondAddress } =
        await loadFixture(deployEnergyTokenFixture);
      await energyToken
        .connect(owner)
        .addProducer(await secondAddress.getAddress());
      await expect(
        energyToken
          .connect(firstAddress)
          .removeProducer(await secondAddress.getAddress())
      ).to.be.revertedWithCustomError(
        energyToken,
        "OwnableUnauthorizedAccount"
      );
    });

    it("Should allow authorized producer to mint tokens", async function () {
      const { energyToken, firstAddress, owner, secondAddress } =
        await loadFixture(deployEnergyTokenFixture);

      await energyToken
        .connect(owner)
        .addProducer(await firstAddress.getAddress());
      await energyToken
        .connect(firstAddress)
        .mint(
          await secondAddress.getAddress(),
          hardhat.ethers.parseEther("100")
        );
      expect(
        await energyToken.balanceOf(await secondAddress.getAddress())
      ).to.equal(hardhat.ethers.parseEther("100"));
    });

    it("Should not allow unauthorized producer to mint tokens", async function () {
      const { energyToken, firstAddress, owner, secondAddress } =
        await loadFixture(deployEnergyTokenFixture);
      await expect(
        energyToken
          .connect(firstAddress)
          .mint(
            await secondAddress.getAddress(),
            hardhat.ethers.parseEther("100")
          )
      ).to.be.revertedWith(
        "Only authorized producers or owner can mint tokens"
      );
    });

    it("Should allow owner to mint tokens", async function () {
      const { energyToken, firstAddress, owner } = await loadFixture(
        deployEnergyTokenFixture
      );

      await energyToken
        .connect(owner)
        .mint(
          await firstAddress.getAddress(),
          hardhat.ethers.parseEther("100")
        );
      expect(
        await energyToken.balanceOf(await firstAddress.getAddress())
      ).to.equal(hardhat.ethers.parseEther("100"));
    });

    it("Should emit event when adding a producer", async function () {
      const { energyToken, firstAddress, owner } = await loadFixture(
        deployEnergyTokenFixture
      );

      await expect(
        energyToken.connect(owner).addProducer(await firstAddress.getAddress())
      )
        .to.emit(energyToken, "ProducerAdded")
        .withArgs(await firstAddress.getAddress());
    });

    it("Should emit event when removing a producer", async function () {
      const { energyToken, firstAddress, owner, secondAddress } =
        await loadFixture(deployEnergyTokenFixture);

      await energyToken
        .connect(owner)
        .addProducer(await firstAddress.getAddress());
      await expect(
        energyToken
          .connect(owner)
          .removeProducer(await firstAddress.getAddress())
      )
        .to.emit(energyToken, "ProducerRemoved")
        .withArgs(await firstAddress.getAddress());
    });
  });

  describe("Transferring", function () {
    it("Should transfer tokens between accounts", async function () {
      const { energyToken, firstAddress, secondAddress } = await loadFixture(
        deployEnergyTokenFixture
      );

      await energyToken.mint(await firstAddress.getAddress(), 1000);

      await energyToken
        .connect(firstAddress)
        .transfer(await secondAddress.getAddress(), 500);

      const secondAddressBalance = await energyToken.balanceOf(
        await secondAddress.getAddress()
      );

      expect(secondAddressBalance).to.equal(500);
    });

    it("Should fail to transfer more tokens than available", async function () {
      const { EnergyToken, energyToken, firstAddress, secondAddress } =
        await loadFixture(deployEnergyTokenFixture);

      await energyToken.mint(await firstAddress.getAddress(), 1000);
      await expect(
        energyToken
          .connect(firstAddress)
          .transfer(await secondAddress.getAddress(), 2000)
      ).to.be.revertedWithCustomError(
        { interface: EnergyToken.interface },
        "ERC20InsufficientBalance"
      );
    });
  });

  describe("Burning", function () {
    it("Should burn tokens correctly", async function () {
      const { energyToken, firstAddress } = await loadFixture(
        deployEnergyTokenFixture
      );

      await energyToken.mint(await firstAddress.getAddress(), 1000);
      await energyToken.connect(firstAddress).burn(500);
      const firstAddressBalance = await energyToken.balanceOf(
        await firstAddress.getAddress()
      );
      expect(firstAddressBalance).to.equal(500);
    });
  });
});
