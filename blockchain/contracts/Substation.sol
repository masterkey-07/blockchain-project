// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./EnergyToken.sol";

contract Substation {
    EnergyToken public energyToken;
    mapping(address => bool) public registeredConsumers;

    constructor(address _energyTokenAddress) {
        energyToken = EnergyToken(_energyTokenAddress);
    }

    function registerConsumer(address consumer) external {
        registeredConsumers[consumer] = true;
    }

    function unregisterConsumer(address consumer) external {
        registeredConsumers[consumer] = false;
    }

    function distributeEnergy(address consumer, uint256 amount) external {
        require(registeredConsumers[consumer], "Consumer not registered");

        require(
            energyToken.transferFrom(msg.sender, consumer, amount),
            "Transfer failed"
        );
    }
}
