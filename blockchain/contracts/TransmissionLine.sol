// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./EnergyToken.sol";

contract TransmissionLine {
    EnergyToken public energyToken;
    address public substation;
    uint256 public constant MAX_LOSS_PERCENTAGE = 5; // 5% maximum allowed loss

    constructor(address _energyTokenAddress, address _substation) {
        energyToken = EnergyToken(_energyTokenAddress);
        substation = _substation;
    }

    function transmitEnergy(uint256 amount) external {
        require(
            energyToken.transferFrom(msg.sender, address(this), amount),
            "Transfer failed"
        );

        uint256 loss = (amount * MAX_LOSS_PERCENTAGE) / 100;
        uint256 transmittedAmount = amount - loss;

        energyToken.burn(loss);
        require(
            energyToken.transfer(substation, transmittedAmount),
            "Transfer to substation failed"
        );
    }
}
