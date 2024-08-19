// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./EnergyToken.sol";

contract Producer {
    EnergyToken public energyToken;
    mapping(address => bool) public authorizedProducers;
    mapping(address => bool) public connectedTransmissionLines;

    constructor(address energyTokenAddress) {
        energyToken = EnergyToken(energyTokenAddress);
        authorizedProducers[msg.sender] = true;
    }

    modifier onlyAuthorized() {
        require(authorizedProducers[msg.sender], "Not authorized");
        _;
    }

    function addAuthorizedProducer(address producer) external onlyAuthorized {
        authorizedProducers[producer] = true;
    }

    function removeAuthorizedProducer(
        address producer
    ) external onlyAuthorized {
        authorizedProducers[producer] = false;
    }

    function connectTransmissionLine(
        address transmissionLine
    ) external onlyAuthorized {
        connectedTransmissionLines[transmissionLine] = true;
    }

    function disconnectTransmissionLine(
        address transmissionLine
    ) external onlyAuthorized {
        connectedTransmissionLines[transmissionLine] = false;
    }

    function produceEnergy(
        address transmissionLine,
        uint256 amount
    ) external onlyAuthorized {
        require(
            connectedTransmissionLines[transmissionLine],
            "TransmissionLine not connected"
        );
        energyToken.mint(transmissionLine, amount);
    }
}
