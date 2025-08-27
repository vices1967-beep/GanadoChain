// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/*
  GanadoRegistryUpgradeable
  - Admin/DAO controla parámetros
  - Asocia NFT -> loteToken (ERC20 batch), guarda IPFS hash de la asociación
  - Permite "tokenizar" un animal (quemar NFT? No: mejor "lock" o crear lote y transferir tokens)
  - Ejemplo simple: crea lote ERC20 via GanadoToken.mintByDAO y graba asociación
*/

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

    IGanadoToken public token;
    IAnimalNFT public nft;

    struct Lote {
        uint256 loteId; // id interno
        string ipfsHash; // información del lote
        uint256 amount; // cantidad de tokens emitidos (wei)
        uint256[] animals; // animales asociados
    }

    mapping(uint256 => uint256) public animalToLote; // tokenId -> loteId
    mapping(uint256 => Lote) public lotes;
    uint256 public nextLoteId;

    event LoteCreated(uint256 indexed loteId, uint256 amount, string ipfsHash, address operator);
    event AnimalAssociated(uint256 indexed loteId, uint256 indexed tokenId);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() { _disableInitializers(); }

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

    /**
     * @notice Crear lote y emitir tokens (ejecutado por DAO)
     * @param to dirección que recibe tokens (ej: frigorífico o mercado)
     * @param amount cantidad de tokens a emitir (wei)
     * @param ipfsHash metadatos del lote (IPFS CID)
     */
    function createLote(address to, uint256 amount, string calldata ipfsHash, uint256[] calldata animals) external onlyRole(DAO_ROLE) returns (uint256) {
        uint256 id = nextLoteId++;
        Lote storage l = lotes[id];
        l.loteId = id;
        l.ipfsHash = ipfsHash;
        l.amount = amount;

        // Asociar animales
        for (uint i = 0; i < animals.length; i++) {
            uint256 t = animals[i];
            animalToLote[t] = id;
            l.animals.push(t);
            emit AnimalAssociated(id, t);
        }

        // Mint tokens via GanadoToken (DAO-controlled)
        token.mintByDAO(to, amount, ipfsHash);

        emit LoteCreated(id, amount, ipfsHash, msg.sender);
        return id;
    }

    function getLoteAnimals(uint256 loteId) external view returns (uint256[] memory) {
        return lotes[loteId].animals;
    }

    // UUPS authorize
    function _authorizeUpgrade(address) internal override onlyRole(UPGRADER_ROLE) {}

    uint256[45] private __gap;
}
