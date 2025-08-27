// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlEnumerableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";

contract GanadoTokenUpgradeable is Initializable, ERC20Upgradeable, AccessControlEnumerableUpgradeable, PausableUpgradeable, UUPSUpgradeable {
    bytes32 public constant DAO_ROLE = keccak256("DAO_ROLE"); 
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE"); 
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant UPGRADER_ROLE = keccak256("UPGRADER_ROLE");

    uint256 private _cap;

    mapping(address => uint256) public minterCap;
    mapping(address => uint256) public minterMinted;

    event BatchMinted(address indexed to, uint256 amount, string indexed batchId, address indexed operator);
    event CapUpdated(uint256 newCap);

    constructor() {
        _disableInitializers();
    }

    function initialize(address daoAdmin, uint256 initialSupply, uint256 cap_) public initializer {
        __ERC20_init("GanadoChain Fungible Token", "GFT");
        __AccessControlEnumerable_init();
        __Pausable_init();
        __UUPSUpgradeable_init();

        _grantRole(DEFAULT_ADMIN_ROLE, daoAdmin);
        _grantRole(DAO_ROLE, daoAdmin);
        _grantRole(UPGRADER_ROLE, daoAdmin);
        _grantRole(PAUSER_ROLE, daoAdmin);

        if (initialSupply > 0) {
            _mint(daoAdmin, initialSupply);
        }

        _cap = cap_;
        emit CapUpdated(cap_);
    }

    function pause() external onlyRole(PAUSER_ROLE) { _pause(); }
    function unpause() external onlyRole(PAUSER_ROLE) { _unpause(); }

    function cap() external view returns (uint256) { return _cap; }

    function setCap(uint256 newCap) external onlyRole(DAO_ROLE) {
        _cap = newCap;
        emit CapUpdated(newCap);
    }

    function mintByDAO(address to, uint256 amount, string calldata batchId) external onlyRole(DAO_ROLE) whenNotPaused {
        require(_cap == 0 || totalSupply() + amount <= _cap, "Cap excedido");
        _mint(to, amount);
        emit BatchMinted(to, amount, batchId, msg.sender);
    }

    function mintByMinter(address to, uint256 amount, string calldata batchId) external whenNotPaused onlyRole(MINTER_ROLE) {
        uint256 capFor = minterCap[msg.sender];
        if (capFor > 0) {
            require(minterMinted[msg.sender] + amount <= capFor, "Limite minter excedido"); // <-- acento eliminado
        }
        require(_cap == 0 || totalSupply() + amount <= _cap, "Cap excedido");
        minterMinted[msg.sender] += amount;
        _mint(to, amount);
        emit BatchMinted(to, amount, batchId, msg.sender);
    }

    function setMinterCap(address minter, uint256 cap_) external onlyRole(DAO_ROLE) {
        minterCap[minter] = cap_;
    }

    function _beforeTokenTransfer(address from, address to, uint256 amount) internal override whenNotPaused {
        super._beforeTokenTransfer(from, to, amount);
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyRole(UPGRADER_ROLE) {}

    uint256[45] private __gap;
}
