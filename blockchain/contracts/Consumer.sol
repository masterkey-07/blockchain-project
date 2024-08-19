// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./EnergyToken.sol";

contract ConsumerContract {
    EnergyToken public energyToken;
    address public owner;

    constructor(address tokenAddress) {
        energyToken = EnergyToken(tokenAddress);
        owner = msg.sender;
    }

    function requestEnergy(address producer, uint256 energyAmount) external {
        require(msg.sender == owner, "Only the owner can request energy");
        energyToken.transferFrom(producer, owner, energyAmount); // Transfer energy tokens from producer to consumer
    }

    function consumeEnergy(uint256 energyAmount) external {
        require(msg.sender == owner, "Only the owner can consume energy");
        energyToken.burn(energyAmount); // Burn the tokens as the energy is consumed
    }
}
