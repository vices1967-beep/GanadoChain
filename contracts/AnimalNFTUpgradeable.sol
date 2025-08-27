// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/*
  AnimalNFTUpgradeable
  - Token ERC721 upgradeable por animal
  - tokenURI público (IPFS) para consumidor
  - registros on-chain mínimos: ipfs hashes, owner history (eventos)
  - AccessControl: PRODUCER_ROLE, VET_ROLE, FRIGORIFICO_ROLE, AUDITOR_ROLE, UPGRADER_ROLE, PAUSER_ROLE
*/

import "@openzeppelin/contracts-upgradeable/token/ERC721/extensions/ERC721URIStorageUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlEnumerableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/utils/StringsUpgradeable.sol"; // <-- CORRECCIÓN

contract AnimalNFTUpgradeable is Initializable, ERC721URIStorageUpgradeable, AccessControlEnumerableUpgradeable, PausableUpgradeable, UUPSUpgradeable {
    using StringsUpgradeable for uint256; // <-- CORRECCIÓN

    bytes32 public constant PRODUCER_ROLE = keccak256("PRODUCER_ROLE");
    bytes32 public constant VET_ROLE = keccak256("VET_ROLE");
    bytes32 public constant FRIGORIFICO_ROLE = keccak256("FRIGORIFICO_ROLE");
    bytes32 public constant AUDITOR_ROLE = keccak256("AUDITOR_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant UPGRADER_ROLE = keccak256("UPGRADER_ROLE");

    uint256 private _nextId;

    // Estructura de metadatos operativos (guardamos solo IPFS CIDs)
    struct AnimalRecord {
        string publicMetadata;      // tokenURI (ipfs://CID)
        string operationalSnapshot; // ipfs hash con datos IoT/GPS/salud
        string processingData;      // ipfs hash de faena/frigorífico
    }

    mapping(uint256 => AnimalRecord) private records;

    // Eventos para indexado
    event AnimalMinted(uint256 indexed tokenId, address indexed owner, string tokenURI);
    event OperationalUpdated(uint256 indexed tokenId, string ipfsHash);
    event ProcessingUpdated(uint256 indexed tokenId, string ipfsHash);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() { _disableInitializers(); }

    function initialize(address admin) public initializer {
        __ERC721_init("GanadoChain Animal NFT", "GANFT");
        __ERC721URIStorage_init();
        __AccessControlEnumerable_init();
        __Pausable_init();
        __UUPSUpgradeable_init();

        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(PAUSER_ROLE, admin);
        _grantRole(UPGRADER_ROLE, admin);

        _nextId = 1;
    }

    function pause() external onlyRole(PAUSER_ROLE) { _pause(); }
    function unpause() external onlyRole(PAUSER_ROLE) { _unpause(); }

    // Mint (solo producers)
    function mintAnimal(address to, string calldata tokenURI_, string calldata operationalIpfs) external whenNotPaused onlyRole(PRODUCER_ROLE) returns (uint256) {
        uint256 tokenId = _nextId++;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, tokenURI_);
        records[tokenId] = AnimalRecord({ publicMetadata: tokenURI_, operationalSnapshot: operationalIpfs, processingData: "" });

        emit AnimalMinted(tokenId, to, tokenURI_);
        return tokenId;
    }

    function updateOperational(uint256 tokenId, string calldata ipfsHash) external whenNotPaused {
        require(_exists(tokenId), "No existe token");
        require(hasRole(PRODUCER_ROLE, msg.sender) || hasRole(VET_ROLE, msg.sender), "No permitido");
        records[tokenId].operationalSnapshot = ipfsHash;
        emit OperationalUpdated(tokenId, ipfsHash);
    }

    function updateProcessing(uint256 tokenId, string calldata ipfsHash) external whenNotPaused onlyRole(FRIGORIFICO_ROLE) {
        require(_exists(tokenId), "No existe token");
        records[tokenId].processingData = ipfsHash;
        emit ProcessingUpdated(tokenId, ipfsHash);
    }

    // Vista para auditores
    function auditView(uint256 tokenId) external view onlyRole(AUDITOR_ROLE) returns (string memory, string memory, string memory) {
        require(_exists(tokenId), "No existe token");
        AnimalRecord memory r = records[tokenId];
        return (tokenURI(tokenId), r.operationalSnapshot, r.processingData);
    }

    // Vista pública
    function publicView(uint256 tokenId) external view returns (string memory) {
        require(_exists(tokenId), "No existe token");
        return tokenURI(tokenId);
    }

    // UUPS authorize
    function _authorizeUpgrade(address) internal override onlyRole(UPGRADER_ROLE) {}

    // hooks
    function _beforeTokenTransfer(address from, address to, uint256 tokenId, uint256 batchSize) internal override {
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
    }

    function supportsInterface(bytes4 interfaceId) public view override(ERC721URIStorageUpgradeable, AccessControlEnumerableUpgradeable) returns (bool) {
        return super.supportsInterface(interfaceId);
    }

    uint256[45] private __gap;
}
