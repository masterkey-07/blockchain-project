// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./EnergyToken.sol";

contract Producer {
    EnergyToken public energyToken;
    address public owner;

    constructor(address energyTokenAddress) {
        energyToken = EnergyToken(energyTokenAddress);
        owner = msg.sender;
    }

    function produceEnergy(address transmissionLine, uint256 amount) external {
        require(msg.sender == owner, "Only the owner can produce energy");
        energyToken.mint(transmissionLine, amount);
    }
}
