// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/access/AccessControlEnumerableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";

interface IGanadoToken {
    function mintByDAO(address to, uint256 amount, string calldata batchId) external;
}

interface IAnimalNFT {
    function ownerOf(uint256 tokenId) external view returns (address);
}

contract GanadoRegistryUpgradeable is Initializable, AccessControlEnumerableUpgradeable, UUPSUpgradeable {
    bytes32 public constant DAO_ROLE = keccak256("DAO_ROLE");
    bytes32 public constant UPGRADER_ROLE = keccak256("UPGRADER_ROLE");
    bytes32 public constant PRODUCER_ROLE = keccak256("PRODUCER_ROLE");
    bytes32 public constant VET_ROLE = keccak256("VET_ROLE");
    bytes32 public constant FRIGORIFICO_ROLE = keccak256("FRIGORIFICO_ROLE");
    bytes32 public constant AUDITOR_ROLE = keccak256("AUDITOR_ROLE");
    bytes32 public constant IOT_ROLE = keccak256("IOT_ROLE");

    IGanadoToken public token;
    IAnimalNFT public nft;

    struct Lote {
        uint256 loteId;
        string ipfsHash;
        uint256 amount;
        uint256[] animals;
        string status; // ← NUEVO CAMPO AGREGADO
    }

    struct IoTData {
        uint256 timestamp;
        string deviceId;
        string dataHash;
        string metadata;
    }

    mapping(uint256 => IoTData[]) private _animalIoTData;
    mapping(uint256 => uint256) public animalToLote;
    mapping(uint256 => Lote) public lotes;
    uint256 public nextLoteId;

    // ← NUEVO EVENTO AGREGADO
    event BatchStatusUpdated(
        uint256 indexed batchId,
        string newStatus,
        bytes32 batchHash,
        uint256 timestamp
    );
    
    event LoteCreated(uint256 indexed loteId, uint256 amount, string ipfsHash, address operator);
    event AnimalAssociated(uint256 indexed loteId, uint256 indexed tokenId);
    event IoTDataRegistered(uint256 indexed animalId, string deviceId, string dataHash, string metadata, uint256 timestamp);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(address daoAdmin, address tokenAddr, address nftAddr) public initializer {
        __AccessControlEnumerable_init();
        __UUPSUpgradeable_init();

        _grantRole(DEFAULT_ADMIN_ROLE, daoAdmin);
        _grantRole(DAO_ROLE, daoAdmin);
        _grantRole(UPGRADER_ROLE, daoAdmin);

        token = IGanadoToken(tokenAddr);
        nft = IAnimalNFT(nftAddr);
        nextLoteId = 1;
    }

    // ← NUEVA FUNCIÓN AGREGADA
    function updateBatchStatus(
        uint256 batchId, 
        string calldata newStatus, 
        bytes32 batchHash
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(batchId > 0 && batchId < nextLoteId, "Invalid batch ID");
        require(bytes(newStatus).length > 0, "Status cannot be empty");
        
        // Actualizar el estado del lote
        lotes[batchId].status = newStatus;
        
        // Emitir evento
        emit BatchStatusUpdated(batchId, newStatus, batchHash, block.timestamp);
    }

    function createLote(address to, uint256 amount, string calldata ipfsHash, uint256[] calldata animals) external onlyRole(DAO_ROLE) returns (uint256) {
        uint256 id = nextLoteId++;
        Lote storage l = lotes[id];
        l.loteId = id;
        l.ipfsHash = ipfsHash;
        l.amount = amount;
        l.status = "created"; // ← ESTADO INICIAL POR DEFECTO

        for (uint i = 0; i < animals.length; i++) {
            uint256 t = animals[i];
            animalToLote[t] = id;
            l.animals.push(t);
            emit AnimalAssociated(id, t);
        }

        token.mintByDAO(to, amount, ipfsHash);
        emit LoteCreated(id, amount, ipfsHash, msg.sender);
        return id;
    }

    function registerIoTData(uint256 animalId, string calldata deviceId, string calldata dataHash, string calldata metadata) external onlyRole(IOT_ROLE) {
        IoTData memory entry = IoTData({ timestamp: block.timestamp, deviceId: deviceId, dataHash: dataHash, metadata: metadata });
        _animalIoTData[animalId].push(entry);
        emit IoTDataRegistered(animalId, deviceId, dataHash, metadata, entry.timestamp);
    }

    function _authorizeUpgrade(address) internal override onlyRole(UPGRADER_ROLE) {}

    uint256[45] private __gap;
}