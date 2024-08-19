// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./EnergyToken.sol";

contract Consumer {
    EnergyToken public energyToken;
    mapping(address => bool) public approvedSubstations;

    constructor(address _energyTokenAddress) {
        energyToken = EnergyToken(_energyTokenAddress);
    }

    function approveSubstation(address substation) external {
        approvedSubstations[substation] = true;
    }

    function revokeSubstationApproval(address substation) external {
        approvedSubstations[substation] = false;
    }

    function consumeEnergy(uint256 amount) external {
        require(approvedSubstations[msg.sender], "Unapproved substation");
        require(
            energyToken.balanceOf(address(this)) >= amount,
            "Insufficient energy tokens"
        );

        energyToken.burn(amount);
    }
}
