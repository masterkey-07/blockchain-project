// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./EnergyToken.sol";

contract Substation {
    EnergyToken public energyToken;
    mapping(address => bool) public registeredConsumers;
    mapping(address => bool) public authorizedOperators;

    constructor(address _energyTokenAddress) {
        energyToken = EnergyToken(_energyTokenAddress);
        authorizedOperators[msg.sender] = true;
    }

    modifier onlyAuthorized() {
        require(authorizedOperators[msg.sender], "Not authorized");
        _;
    }

    function addAuthorizedOperator(address operator) external onlyAuthorized {
        authorizedOperators[operator] = true;
    }

    function removeAuthorizedOperator(
        address operator
    ) external onlyAuthorized {
        authorizedOperators[operator] = false;
    }

    function registerConsumer(address consumer) external onlyAuthorized {
        registeredConsumers[consumer] = true;
    }

    function unregisterConsumer(address consumer) external onlyAuthorized {
        registeredConsumers[consumer] = false;
    }

    function distributeEnergy(
        address consumer,
        uint256 amount
    ) external onlyAuthorized {
        require(registeredConsumers[consumer], "Consumer not registered");
        require(
            energyToken.transferFrom(msg.sender, consumer, amount),
            "Transfer failed"
        );
    }
}
