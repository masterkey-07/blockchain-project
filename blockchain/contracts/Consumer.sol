// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./EnergyToken.sol";

contract Consumer {
    EnergyToken public energyToken;
    mapping(address => bool) public authorizedManagers;

    constructor(address _energyTokenAddress) {
        energyToken = EnergyToken(_energyTokenAddress);
        authorizedManagers[msg.sender] = true;
    }

    modifier onlyAuthorized() {
        require(authorizedManagers[msg.sender], "Not authorized");
        _;
    }

    function addAuthorizedManager(address manager) external onlyAuthorized {
        authorizedManagers[manager] = true;
    }

    function removeAuthorizedManager(address manager) external onlyAuthorized {
        authorizedManagers[manager] = false;
    }

    function consumeEnergy(uint256 amount) external onlyAuthorized {
        require(
            energyToken.balanceOf(msg.sender) >= amount,
            "Insufficient energy tokens"
        );

        energyToken.transferFrom(msg.sender, address(this), amount);
        energyToken.burn(amount);
    }
}
