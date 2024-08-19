// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./EnergyToken.sol";

contract ProducerContract {
    EnergyToken public energyToken;
    address public owner;

    constructor(address tokenAddress) {
        energyToken = EnergyToken(tokenAddress);
        owner = msg.sender;
    }

    function produceEnergy(uint256 energyAmount) external {
        require(msg.sender == owner, "Only the owner can produce energy");
        energyToken.mint(owner, energyAmount); // Mint energy tokens to the producer
    }

    function offerEnergy(address consumer, uint256 energyAmount) external {
        require(msg.sender == owner, "Only the owner can offer energy");
        require(
            energyToken.balanceOf(owner) >= energyAmount,
            "Insufficient energy tokens"
        );

        energyToken.transfer(consumer, energyAmount); // Transfer energy tokens to the consumer
    }
}
