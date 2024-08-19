// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract EnergyToken is ERC20, Ownable {
    mapping(address => bool) public authorizedProducers;

    event ProducerAdded(address indexed producer);
    event ProducerRemoved(address indexed producer);

    constructor() ERC20("EnergyToken", "ENG") Ownable(msg.sender) {}

    function addProducer(address producer) external onlyOwner {
        authorizedProducers[producer] = true;
        emit ProducerAdded(producer);
    }

    function removeProducer(address producer) external onlyOwner {
        authorizedProducers[producer] = false;
        emit ProducerRemoved(producer);
    }

    function mint(address to, uint256 amount) external {
        require(
            authorizedProducers[msg.sender] || msg.sender == owner(),
            "Only authorized producers or owner can mint tokens"
        );
        _mint(to, amount);
    }

    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }
}
