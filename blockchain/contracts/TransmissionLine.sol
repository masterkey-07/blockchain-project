// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./EnergyToken.sol";

contract TransmissionLineContract {
    EnergyToken public energyToken;
    address public owner;

    // Events for logging
    event EnergyTransferred(
        address indexed producer,
        address indexed substation,
        uint256 amount
    );

    constructor(address energyTokenAddress) {
        energyToken = EnergyToken(energyTokenAddress);
        owner = msg.sender;
    }

    // Function to transfer energy tokens from a producer to the substation
    function transferEnergyToSubstation(
        address producer,
        address substation,
        uint256 amount
    ) external {
        require(
            msg.sender == owner,
            "Only the owner can initiate the transfer"
        );
        require(
            energyToken.balanceOf(producer) >= amount,
            "Producer has insufficient energy tokens"
        );

        // Transfer energy tokens from the producer to the substation
        energyToken.transferFrom(producer, substation, amount);

        // Emit an event for tracking the transfer
        emit EnergyTransferred(producer, substation, amount);
    }

    // Function to check the balance of energy tokens for a producer
    function checkProducerBalance(
        address producer
    ) external view returns (uint256) {
        return energyToken.balanceOf(producer);
    }

    // Function to check the balance of energy tokens for a substation
    function checkSubstationBalance(
        address substation
    ) external view returns (uint256) {
        return energyToken.balanceOf(substation);
    }
}
