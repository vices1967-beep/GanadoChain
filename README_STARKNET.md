# 🥩 BeefChain - Traceability Anchored on Bitcoin

**A hybrid blockchain architecture (StarkNet + Bitcoin) for premium meat traceability.**  
*Winner of the Bitcoin Unleashed Track at the StarkNet Hackathon*

[![StarkNet](https://img.shields.io/badge/StarkNet-%5E0.9.0-ff69b4)](https://starknet.io/)
[![Bitcoin](https://img.shields.io/badge/Bitcoin-Atomiq%20Protocol-orange)](https://atomiq.xyz/)
[![Xverse](https://img.shields.io/badge/Wallet-Xverse-green)](https://www.xverse.app/)
[![Django](https://img.shields.io/badge/Backend-Django%204.2-success)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/Frontend-React%2FVite-blue)](https://reactjs.org/)

![BeefChain Architecture](https://raw.githubusercontent.com/vices1967-beep/GanadoChain/main/backend/static/images/architecture.png)  
*Hybrid Architecture: StarkNet for scalable operations + Bitcoin for immutable certification*

## 🏆 Hackathon Focus: Bitcoin Unleashed Track

This project demonstrates a novel hybrid approach for supply chain traceability:
- **StarkNet Layer:** Handles high-volume, low-cost operations (animal registration, IoT data, status changes).
- **Bitcoin Layer:** Provides ultimate immutability for final certification using the **Atomiq Protocol** and **Xverse wallets**.

## 🚀 Key Innovation: The Bitcoin Certification Flow

This is the core demo flow for the hackathon:

1.  **Request Certification:** A producer requests Bitcoin certification for a batch (`request_btc_certification`).
2.  **StarkNet Event:** The `GanadoRegistry` contract emits a `LoteCertified` event.
3.  **Oracle Listens:** A Django-based oracle listens for the event.
4.  **Mint on Bitcoin:** The oracle mints a certification NFT on Bitcoin testnet using Atomiq.
5.  **Anchor Proof:** The Bitcoin transaction hash is recorded back on StarkNet.
6.  **Consumer Verification:** End-users scan a QR code to verify the entire history, capped by the Bitcoin proof.

## 🛠️ Project Structure

GanadoChain/
├── backend/ # Django REST API (Oracle + Data Indexer)
├── frontend/ # React/Vite Demo App
├── starknet/ # StarkNet Contracts (Cairo) NEW FOR HACKATHON
│ ├── contracts/src/
│ │ ├── AnimalNFT.cairo # Minimalist animal registry
│ │ └── GanadoRegistry.cairo # Core BTC certification logic
│ ├── scripts/ # Deployment scripts
│ └── scarb.toml
└── hardhat/ # Legacy Polygon contracts (for reference)


## ⚡ Quick Start: Experience the Demo

Follow these steps to see the Bitcoin integration in action:

### Prerequisites
- Python 3.10+, Node.js, Docker
- An Xverse wallet (testnet)
- [StarkNet CLI](https://starknet.io/)

### 1. Clone and Setup
```bash
git clone https://github.com/vices1967-beep/GanadoChain
cd GanadoChain
# Setup backend (Django)
cd backend && pip install -r requirements.txt
# Setup frontend (React)
cd ../frontend && npm install
# Setup StarkNet contracts
cd ../starknet && scarb build

2. Run the Oracle & Demo
bash

# Terminal 1: Start the Django Oracle
cd backend
python manage.py runserver

# Terminal 2: Start the Event Listener
python manage.py listen_btc

# Terminal 3: Start the React Demo
cd frontend
npm run dev

3. Experience the Bitcoin Flow

    Open the React app: http://localhost:5173

    Go to the Admin Demo tab

    Select a batch and click "Certify on Bitcoin"

    Watch the terminal for the Oracle minting the Bitcoin NFT

    Scan the generated QR code on the Verify tab to see the Bitcoin proof!

## 📱 Demo Video

https://img.youtube.com/vi/TODO_ADD_VIDEO_ID/0.jpg
# 🔮 Future Vision

This hackathon MVP focuses on the certification flow. The full vision includes:

    Automatic revenue sharing between supply chain participants

    Token-based governance for standards

    Zero-knowledge proofs for private data verification

    Decentralized IoT data oracles

Explore the feature-rich branch for work-in-progress on these features.
###👨‍💻 Team

    Victor Viceconti - Industrial Eng / Full Stack Dev (GitHub)

## 🎯 Hackathon Submission

This project is submitted to the StarkNet Hackathon Fall 2024 in the Bitcoin Unleashed track, utilizing:

    ✅ StarkNet for scalable operations

    ✅ Atomiq Protocol for Bitcoin-based assets

    ✅ Xverse for Bitcoin wallet integration

    ✅ Vesu for mobile-first experience (React app)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.