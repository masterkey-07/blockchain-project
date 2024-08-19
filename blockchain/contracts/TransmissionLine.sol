// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./EnergyToken.sol";

contract TransmissionLine {
    EnergyToken public energyToken;
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

    function transmitEnergy(
        address to,
        uint256 amount
    ) external onlyAuthorized {
        require(
            energyToken.transferFrom(msg.sender, to, amount),
            "Transfer failed"
        );
    }
}
