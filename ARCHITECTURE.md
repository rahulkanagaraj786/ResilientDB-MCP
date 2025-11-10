# ResilientDB MCP Server Architecture

## Overview

The ResilientDB MCP Server is a Model Context Protocol (MCP) implementation that provides a standardized interface for AI agents to interact with ResilientDB blockchain. It bridges the gap between MCP hosts (like Claude Desktop) and ResilientDB's backend services.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Host (Claude Desktop)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ MCP Protocol (stdio)
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    ResilientDB MCP Server                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    MCP Server Core                        │  │
│  │  - Tool Registration                                     │  │
│  │  - Request Routing                                       │  │
│  │  - Error Handling                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│        ┌────────────────────┼────────────────────┐              │
│        │                    │                    │              │
│  ┌─────▼──────┐    ┌────────▼────────┐  ┌───────▼───────┐     │
│  │ GraphQL    │    │ ResContract CLI │  │ Configuration │     │
│  │ Client     │    │ Client          │  │ Manager       │     │
│  └─────┬──────┘    └────────┬────────┘  └───────────────┘     │
│        │                    │                                    │
└────────┼────────────────────┼────────────────────────────────────┘
         │                    │
         │ HTTP/GraphQL       │ CLI Commands
         │                    │
┌────────▼────────────────────▼────────────────────────────────────┐
│                    ResilientDB Backend                            │
│  ┌──────────────────┐              ┌──────────────────────┐     │
│  │ GraphQL Server   │              │ ResContract Service  │     │
│  │ - Account Mgmt   │              │ - Compile Contracts  │     │
│  │ - Transactions   │              │ - Deploy Contracts   │     │
│  │ - Key-Value Ops  │              │ - Execute Contracts  │     │
│  └──────────────────┘              └──────────────────────┘     │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              ResilientDB Blockchain                       │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
```

## Components

### 1. MCP Server Core (`server.py`)

The main server component that:
- Registers all available tools with the MCP protocol
- Handles incoming tool calls from MCP hosts
- Routes requests to appropriate clients
- Manages error handling and response formatting

**Key Responsibilities:**
- Tool registration and discovery
- Request validation
- Response formatting
- Error handling and reporting

### 2. GraphQL Client (`graphql_client.py`)

Handles all GraphQL-based operations:
- Account creation and management
- Transaction operations (get, post, update)
- Key-value store operations
- Query execution and error handling

**Operations:**
- `create_account()` - Create new accounts
- `get_transaction()` - Retrieve transactions
- `post_transaction()` - Submit new transactions
- `update_transaction()` - Update existing transactions
- `get_key_value()` - Retrieve key-value pairs
- `set_key_value()` - Store key-value pairs

### 3. ResContract CLI Client (`rescontract_client.py`)

Handles smart contract operations via ResContract CLI:
- Contract compilation
- Contract deployment
- Contract execution (read/write)
- Contract state retrieval
- Transaction queries

**Operations:**
- `compile_contract()` - Compile smart contracts
- `deploy_contract()` - Deploy contracts to blockchain
- `execute_contract()` - Execute contract methods
- `get_contract_state()` - Retrieve contract state
- `get_transaction()` - Query transactions via CLI

### 4. Configuration Manager (`config.py`)

Manages server configuration:
- Environment variable loading
- Configuration validation
- Default value management

**Configuration Options:**
- GraphQL endpoint URL
- ResContract CLI path
- Authentication tokens
- Timeout settings
- Polling configuration

## Request Flow

### Smart Contract Operations

1. **MCP Host** sends tool call (e.g., `compileContract`)
2. **MCP Server** receives and validates request
3. **ResContract Client** executes CLI command
4. **ResContract CLI** processes command
5. **Response** flows back through the chain

### GraphQL Operations

1. **MCP Host** sends tool call (e.g., `createAccount`)
2. **MCP Server** receives and validates request
3. **GraphQL Client** constructs and executes query
4. **GraphQL Server** processes request
5. **Response** flows back through the chain

### Hybrid Operations

1. **MCP Host** sends tool call (e.g., `getTransaction`)
2. **MCP Server** receives request
3. **GraphQL Client** attempts operation first
4. If GraphQL fails, **ResContract Client** is used as fallback
5. **Response** is returned to MCP host

## Routing Logic

The server uses operation-based routing:

| Operation | Service | Fallback |
|-----------|---------|----------|
| `compileContract` | ResContract CLI | - |
| `deployContract` | ResContract CLI | - |
| `executeContract` | ResContract CLI | - |
| `getContractState` | ResContract CLI | - |
| `createAccount` | GraphQL | - |
| `postTransaction` | GraphQL | - |
| `updateTransaction` | GraphQL | - |
| `get` | GraphQL | - |
| `set` | GraphQL | - |
| `getTransaction` | GraphQL | ResContract CLI |

## Error Handling

### Error Types

1. **Configuration Errors**: Missing or invalid configuration
2. **GraphQL Errors**: API request failures, query errors
3. **ResContract Errors**: CLI command failures, file not found
4. **Network Errors**: Connection timeouts, unreachable services
5. **Validation Errors**: Invalid parameters, missing required fields

### Error Flow

1. Error occurs in client layer
2. Exception is caught and formatted
3. Error details are included in response
4. MCP host receives structured error response

## Data Flow

### Request Processing

```
MCP Request → Validation → Route Selection → Client Execution → Response Formatting → MCP Response
```

### Response Format

All responses are formatted as JSON:
```json
{
  "data": {...},
  "error": null
}
```

Error responses:
```json
{
  "error": {
    "type": "ErrorType",
    "message": "Error message",
    "details": {...}
  }
}
```

## Security Considerations

1. **Authentication**: Optional API keys and tokens via environment variables
2. **Input Validation**: All inputs are validated before processing
3. **Error Messages**: Sensitive information is not exposed in error messages
4. **Network Security**: HTTPS should be used for GraphQL endpoints
5. **CLI Security**: ResContract CLI commands are executed in controlled environment

## Performance Considerations

1. **Async Operations**: All I/O operations are asynchronous
2. **Connection Pooling**: HTTP clients use connection pooling
3. **Timeout Management**: Configurable timeouts prevent hanging requests
4. **Error Recovery**: Fallback mechanisms for hybrid operations
5. **Resource Management**: Proper cleanup of resources

## Extension Points

The architecture supports extension through:

1. **New Tools**: Add new tools by registering them in `server.py`
2. **New Clients**: Add new client implementations for additional services
3. **Custom Routing**: Modify routing logic in `server.py`
4. **Middleware**: Add middleware for logging, metrics, etc.
5. **Plugins**: Support for plugin-based extensions

## Testing Strategy

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete request flows
4. **Mock Services**: Use mocks for external dependencies
5. **Error Scenarios**: Test error handling and recovery

## Deployment Considerations

1. **Docker**: Containerized deployment for consistency
2. **Environment Variables**: Configuration via environment variables
3. **Health Checks**: Monitor server health and status
4. **Logging**: Comprehensive logging for debugging
5. **Monitoring**: Metrics and monitoring for production use

## Future Enhancements

1. **Caching**: Add caching layer for frequently accessed data
2. **Rate Limiting**: Implement rate limiting for API calls
3. **Batch Operations**: Support for batch operations
4. **WebSocket Support**: Real-time updates via WebSockets
5. **Advanced Routing**: More sophisticated routing logic
6. **Metrics**: Detailed metrics and analytics
7. **Authentication**: Enhanced authentication mechanisms

