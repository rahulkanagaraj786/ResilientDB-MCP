# ResilientDB MCP Server

A Model Context Protocol (MCP) server for interacting with ResilientDB, a high-performance blockchain platform. This server allows Large Language Models (LLMs) like Claude to interact with ResilientDB through smart contract operations and GraphQL queries.

## Overview

This MCP server bridges the gap between AI agents (like Claude Desktop) and ResilientDB by providing a standardized interface for:
- **Smart Contract Operations**: Compile, deploy, and execute smart contracts using ResContract CLI
- **GraphQL Operations**: Create accounts, manage transactions, and query data
- **Key-Value Operations**: Store and retrieve data using ResilientDB's key-value store

## Features

### Smart Contract Operations
- `compileContract`: Compile smart contracts using ResContract CLI
- `deployContract`: Deploy compiled contracts to the ResilientDB blockchain
- `executeContract`: Execute contract methods (read/write operations)
- `getContractState`: Retrieve the current state of a deployed contract

### GraphQL Operations
- `createAccount`: Create new accounts in ResilientDB
- `getTransaction`: Retrieve transaction details by ID
- `postTransaction`: Post new transactions to the blockchain
- `updateTransaction`: Update existing transactions

### Key-Value Operations
- `get`: Retrieve values by key
- `set`: Store key-value pairs

## Installation

### Prerequisites

- Python 3.11 or higher
- ResilientDB instance running (see [ResilientDB Installation](https://github.com/apache/incubator-resilientdb))
- ResContract CLI installed (for smart contract operations)
- Access to ResilientDB GraphQL endpoint

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/rahulkanagaraj786/ResilientDB-MCP.git
cd ResilientDB-MCP
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your ResilientDB configuration
```

4. Update `.env` file with your settings:
```env
RESILIENTDB_GRAPHQL_URL=http://localhost:9000/graphql
RESCONTRACT_CLI_PATH=rescontract
```

### Docker Installation

1. Build the Docker image:
```bash
docker build -t mcp/resilientdb -f Dockerfile .
```

2. Run the container:
```bash
docker run -i --rm mcp/resilientdb
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RESILIENTDB_GRAPHQL_URL` | GraphQL endpoint URL | `http://localhost:9000/graphql` |
| `RESCONTRACT_CLI_PATH` | Path to ResContract CLI executable | `rescontract` |
| `RESILIENTDB_API_KEY` | Optional API key for authentication | None |
| `RESILIENTDB_AUTH_TOKEN` | Optional auth token | None |
| `REQUEST_TIMEOUT` | Request timeout in seconds | `30` |
| `TRANSACTION_POLL_INTERVAL` | Polling interval for transactions | `1.0` |
| `MAX_POLL_ATTEMPTS` | Maximum polling attempts | `30` |

## Usage with Claude Desktop

Add the MCP server to your Claude Desktop configuration:

1. Open Claude Desktop settings
2. Edit the MCP servers configuration file (usually `claude_desktop.json`)
3. Add the following configuration:

### For Local Installation:
```json
{
  "mcpServers": {
    "resilientdb": {
      "command": "python",
      "args": ["/path/to/ResilientDB-MCP/server.py"],
      "env": {
        "RESILIENTDB_GRAPHQL_URL": "http://localhost:9000/graphql",
        "RESCONTRACT_CLI_PATH": "rescontract"
      }
    }
  }
}
```

### For Docker Installation:
```json
{
  "mcpServers": {
    "resilientdb": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp/resilientdb"]
    }
  }
}
```

4. Restart Claude Desktop

## Available Tools

### createAccount
Create a new account in ResilientDB.

**Parameters:**
- `accountId` (optional): Account ID. If not provided, server will generate one.

**Example:**
```json
{
  "accountId": "my-account-123"
}
```

### compileContract
Compile a smart contract using ResContract CLI.

**Parameters:**
- `contractPath` (required): Path to the contract file
- `outputDir` (optional): Output directory for compiled contract

**Example:**
```json
{
  "contractPath": "/path/to/contract.sol",
  "outputDir": "/path/to/output"
}
```

### deployContract
Deploy a compiled smart contract to ResilientDB.

**Parameters:**
- `contractPath` (required): Path to the compiled contract
- `accountId` (optional): Account ID for deployment
- `constructorArgs` (optional): Constructor arguments

**Example:**
```json
{
  "contractPath": "/path/to/compiled_contract.json",
  "accountId": "my-account-123",
  "constructorArgs": ["arg1", "arg2"]
}
```

### executeContract
Execute a method on a deployed smart contract.

**Parameters:**
- `contractAddress` (required): Address of the deployed contract
- `methodName` (required): Name of the method to execute
- `methodArgs` (optional): Method arguments
- `accountId` (optional): Account ID for execution
- `transactionType` (optional): "call" for read operations, "send" for write operations (default: "call")

**Example:**
```json
{
  "contractAddress": "0x123...",
  "methodName": "getValue",
  "transactionType": "call"
}
```

### getTransaction
Get transaction details by transaction ID.

**Parameters:**
- `transactionId` (required): Transaction ID to retrieve

**Example:**
```json
{
  "transactionId": "tx-123456"
}
```

### postTransaction
Post a new transaction to ResilientDB.

**Parameters:**
- `data` (required): Transaction data as key-value pairs

**Example:**
```json
{
  "data": {
    "key": "value",
    "amount": 100
  }
}
```

### updateTransaction
Update an existing transaction.

**Parameters:**
- `transactionId` (required): Transaction ID to update
- `data` (required): Updated transaction data

**Example:**
```json
{
  "transactionId": "tx-123456",
  "data": {
    "status": "completed"
  }
}
```

### get
Retrieve a value from ResilientDB by key.

**Parameters:**
- `key` (required): Key to retrieve

**Example:**
```json
{
  "key": "my-key"
}
```

### set
Store a key-value pair in ResilientDB.

**Parameters:**
- `key` (required): Key to store
- `value` (required): Value to store

**Example:**
```json
{
  "key": "my-key",
  "value": "my-value"
}
```

### getContractState
Get the current state of a deployed smart contract.

**Parameters:**
- `contractAddress` (required): Address of the deployed contract

**Example:**
```json
{
  "contractAddress": "0x123..."
}
```

## Architecture

The MCP server acts as a mediator between the MCP host (Claude Desktop) and ResilientDB backend services:

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│ Claude      │────────▶│ MCP Server   │────────▶│ ResilientDB │
│ Desktop     │         │ (Python)     │         │ Backend     │
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              ├──▶ GraphQL Client
                              │    (Account, Transaction, KV ops)
                              │
                              └──▶ ResContract CLI
                                   (Smart Contract ops)
```

### Routing Logic

The server automatically routes requests to the appropriate service:
- **Smart Contract Operations** → ResContract CLI
- **Data Operations** → GraphQL API
- **Hybrid Operations** → Tries GraphQL first, falls back to ResContract CLI

## Development

### Project Structure

```
ResilientDB-MCP/
├── server.py              # Main MCP server implementation
├── graphql_client.py      # GraphQL client for ResilientDB
├── rescontract_client.py  # ResContract CLI client
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
└── README.md              # This file
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Troubleshooting

### ResContract CLI Not Found

If you get an error about ResContract CLI not being found:
1. Ensure ResContract CLI is installed
2. Add it to your PATH, or
3. Set `RESCONTRACT_CLI_PATH` environment variable to the full path

### GraphQL Connection Errors

If you encounter GraphQL connection errors:
1. Verify ResilientDB is running
2. Check the `RESILIENTDB_GRAPHQL_URL` is correct
3. Ensure network connectivity to the GraphQL endpoint
4. Check firewall settings

### Transaction Timeouts

If transactions timeout:
1. Increase `REQUEST_TIMEOUT` in `.env`
2. Check ResilientDB blockchain status
3. Verify network latency

## References

- [ResilientDB GitHub](https://github.com/apache/incubator-resilientdb)
- [ResilientDB Documentation](https://resilientdb.incubator.apache.org/)
- [ResContract CLI Documentation](https://beacon.resilientdb.com/docs/rescontract)
- [ResilientDB GraphQL API](https://beacon.resilientdb.com/docs/resilientdb_graphql)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)

## License

Apache 2.0 License

## Authors

Team 10 - ECS 265 Project
