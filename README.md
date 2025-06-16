# Smart Contract Intelligence Platform

A comprehensive platform that bridges the gap between non-technical users and blockchain smart contracts using AI. This system enables users to create, visualize, audit, and deploy smart contracts through natural language instructions.

## Features

- **Natural Language Contract Creation**: Describe what you want in plain English and get a secure smart contract.
- **Contract Visualization**: Interactive flowcharts and simulations to understand how your contract works.
- **Security Auditing**: Automated analysis to identify vulnerabilities and suggest improvements.
- **Contract Library**: Pre-built templates for common use cases like tokens, NFTs, DAOs, and more.
- **One-Click Deployment**: Deploy contracts to any blockchain network with minimal technical knowledge.

## Technology Stack

### Frontend
- React.js with React Router for single-page application
- Tailwind CSS for styling
- Recharts for data visualization
- Web3.js for blockchain interactions

### Backend
- Python FastAPI for the main API
- OpenAI GPT integration for natural language processing
- MongoDB for data storage
- Go for high-performance blockchain operations

### Blockchain
- Solidity for smart contracts
- Ethereum compatibility (can deploy to any EVM-compatible chain)
- Support for popular standards (ERC20, ERC721, etc.)

## Project Structure

```
smart-contract-intelligence/
├── frontend/                      # React frontend
│   ├── public/
│   └── src/
│       ├── assets/
│       ├── components/
│       │   ├── common/
│       │   ├── ContractCreator/
│       │   ├── ContractVisualizer/
│       │   ├── ContractAuditor/
│       │   └── ContractLibrary/
│       ├── contexts/
│       ├── pages/
│       ├── services/
│       ├── styles/
│       ├── App.jsx
│       └── index.js
├── backend/                       # Python backend
│   ├── api/
│   │   ├── routes/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── core/
│   │   ├── utils/
│   │   └── main.py
│   └── requirements.txt
├── blockchain/                    # Go blockchain services
│   ├── cmd/
│   │   └── contractservice/
│   ├── internal/
│   │   ├── contracts/
│   │   ├── audit/
│   │   ├── library/
│   │   └── eth/
│   ├── pkg/
│   │   └── types/
│   └── contracts/
│       └── templates/
├── docker/                        # Containerization
│   ├── frontend.Dockerfile
│   ├── backend.Dockerfile
│   ├── blockchain.Dockerfile
│   └── docker-compose.yml
├── docs/                          # Documentation
└── README.md
```

## Prerequisites

- Docker and Docker Compose
- Node.js 16+ (for local development)
- Python 3.9+ (for local development)
- Go 1.18+ (for local development)
- MongoDB (handled by Docker)
- OpenAI API key

## Setup and Installation

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/smart-contract-intelligence.git
   cd smart-contract-intelligence
   ```

2. Create a `.env` file in the root directory with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SECRET_KEY=your_secret_key_for_jwt
   ETH_RPC_URL=https://mainnet.infura.io/v3/your_infura_key
   ETH_PRIVATE_KEY=your_ethereum_private_key
   ```

3. Start the containers:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup (Development)

#### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env.local` file:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm start
   ```

#### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file:
   ```
   DEBUG=true
   PORT=8000
   MONGODB_URL=mongodb://localhost:27017/smart_contracts
   BLOCKCHAIN_SERVICE_URL=http://localhost:8080
   OPENAI_API_KEY=your_openai_api_key
   SECRET_KEY=your_secret_key_for_jwt
   ```

5. Start the API server:
   ```bash
   uvicorn api.main:app --reload
   ```

#### Blockchain Service

1. Navigate to the blockchain directory:
   ```bash
   cd blockchain
   ```

2. Install dependencies:
   ```bash
   go mod download
   ```

3. Build and run the service:
   ```bash
   go build -o main ./cmd/contractservice
   ./main
   ```

## Usage

### Creating a Smart Contract

1. Log in to the platform
2. Navigate to "Create Contract"
3. Select a contract type (Token, NFT, DAO, etc.)
4. Describe what you want in plain English
5. Customize parameters if needed
6. Generate and review your contract
7. Save or deploy your contract

### Visualizing a Contract

1. Open any contract in your dashboard
2. Navigate to the "Visualize" tab
3. Choose between flowchart, sequence diagram, or interactive simulation
4. Explore the contract's functionality visually

### Auditing a Contract

1. Open any contract in your dashboard
2. Navigate to the "Audit" tab
3. Click "Run Audit" to analyze the contract
4. Review identified vulnerabilities and recommendations
5. Apply suggested fixes if needed

### Deploying a Contract

1. Open any contract in your dashboard
2. Navigate to the "Deploy" tab
3. Select a blockchain network
4. Set constructor parameters if needed
5. Estimate deployment cost
6. Click "Deploy" and confirm the transaction

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- OpenAI for providing the GPT API
- OpenZeppelin for secure smart contract templates
- The Ethereum community for standards and documentation