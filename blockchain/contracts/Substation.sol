// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./EnergyToken.sol";

contract SubstationContract {
    EnergyToken public energyToken;
    address public owner;

    constructor(address tokenAddress) {
        energyToken = EnergyToken(tokenAddress);
        owner = msg.sender;
    }

    function manageTransaction(
        address producer,
        address consumer,
        uint256 energyAmount
    ) external {
        require(msg.sender == owner, "Only the owner can manage transactions");
        require(
            energyToken.balanceOf(producer) >= energyAmount,
            "Producer has insufficient energy tokens"
        );

        energyToken.transferFrom(producer, consumer, energyAmount); // Facilitate the transfer of energy tokens
    }
}
