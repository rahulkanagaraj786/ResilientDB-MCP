"""MCP Server for ResilientDB - Smart Contract and GraphQL integration."""
import asyncio
import json
import sys
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: MCP SDK not found. Please install it with: pip install mcp", file=sys.stderr)
    sys.exit(1)

from config import Config
from graphql_client import GraphQLClient
from rescontract_client import ResContractClient


# Initialize clients
graphql_client = GraphQLClient()
rescontract_client = ResContractClient()

# Create MCP server
app = Server("resilientdb-mcp")


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="createAccount",
            description="Create a new account in ResilientDB. Returns account ID and public key.",
            inputSchema={
                "type": "object",
                "properties": {
                    "accountId": {
                        "type": "string",
                        "description": "Optional account ID. If not provided, server will generate one."
                    }
                }
            }
        ),
        Tool(
            name="compileContract",
            description="Compile a smart contract using ResContract CLI.",
            inputSchema={
                "type": "object",
                "properties": {
                    "contractPath": {
                        "type": "string",
                        "description": "Path to the contract file to compile."
                    },
                    "outputDir": {
                        "type": "string",
                        "description": "Optional output directory for compiled contract."
                    }
                },
                "required": ["contractPath"]
            }
        ),
        Tool(
            name="deployContract",
            description="Deploy a compiled smart contract to ResilientDB blockchain.",
            inputSchema={
                "type": "object",
                "properties": {
                    "contractPath": {
                        "type": "string",
                        "description": "Path to the compiled contract file."
                    },
                    "accountId": {
                        "type": "string",
                        "description": "Optional account ID for deployment."
                    },
                    "constructorArgs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional constructor arguments for the contract."
                    }
                },
                "required": ["contractPath"]
            }
        ),
        Tool(
            name="executeContract",
            description="Execute a method on a deployed smart contract. Use 'call' for read operations, 'send' for write operations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "contractAddress": {
                        "type": "string",
                        "description": "Address of the deployed contract."
                    },
                    "methodName": {
                        "type": "string",
                        "description": "Name of the method to execute."
                    },
                    "methodArgs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional arguments for the method."
                    },
                    "accountId": {
                        "type": "string",
                        "description": "Optional account ID for execution."
                    },
                    "transactionType": {
                        "type": "string",
                        "enum": ["call", "send"],
                        "description": "Transaction type: 'call' for read operations, 'send' for write operations.",
                        "default": "call"
                    }
                },
                "required": ["contractAddress", "methodName"]
            }
        ),
        Tool(
            name="getTransaction",
            description="Get transaction details by transaction ID. Uses GraphQL for queries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "transactionId": {
                        "type": "string",
                        "description": "Transaction ID to retrieve."
                    }
                },
                "required": ["transactionId"]
            }
        ),
        Tool(
            name="postTransaction",
            description="Post a new transaction to ResilientDB using GraphQL.",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "description": "Transaction data as key-value pairs."
                    }
                },
                "required": ["data"]
            }
        ),
        Tool(
            name="updateTransaction",
            description="Update an existing transaction using GraphQL.",
            inputSchema={
                "type": "object",
                "properties": {
                    "transactionId": {
                        "type": "string",
                        "description": "Transaction ID to update."
                    },
                    "data": {
                        "type": "object",
                        "description": "Updated transaction data."
                    }
                },
                "required": ["transactionId", "data"]
            }
        ),
        Tool(
            name="get",
            description="Retrieves a value from ResilientDB by key using GraphQL.",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Key to retrieve."
                    }
                },
                "required": ["key"]
            }
        ),
        Tool(
            name="set",
            description="Stores a key-value pair in ResilientDB using GraphQL.",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Key to store the value under."
                    },
                    "value": {
                        "description": "Value to store (can be any JSON-serializable value)."
                    }
                },
                "required": ["key", "value"]
            }
        ),
        Tool(
            name="getContractState",
            description="Get the current state of a deployed smart contract.",
            inputSchema={
                "type": "object",
                "properties": {
                    "contractAddress": {
                        "type": "string",
                        "description": "Address of the deployed contract."
                    }
                },
                "required": ["contractAddress"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """Handle tool calls and route to appropriate services."""
    if arguments is None:
        arguments = {}
    
    try:
        if name == "createAccount":
            account_id = arguments.get("accountId")
            result = await graphql_client.create_account(account_id)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "compileContract":
            contract_path = arguments["contractPath"]
            output_dir = arguments.get("outputDir")
            result = await rescontract_client.compile_contract(contract_path, output_dir)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "deployContract":
            contract_path = arguments["contractPath"]
            account_id = arguments.get("accountId")
            constructor_args = arguments.get("constructorArgs")
            result = await rescontract_client.deploy_contract(
                contract_path,
                account_id,
                constructor_args
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "executeContract":
            contract_address = arguments["contractAddress"]
            method_name = arguments["methodName"]
            method_args = arguments.get("methodArgs")
            account_id = arguments.get("accountId")
            transaction_type = arguments.get("transactionType", "call")
            result = await rescontract_client.execute_contract(
                contract_address,
                method_name,
                method_args,
                account_id,
                transaction_type
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "getTransaction":
            transaction_id = arguments["transactionId"]
            # Try GraphQL first, fallback to ResContract CLI
            try:
                result = await graphql_client.get_transaction(transaction_id)
            except Exception:
                # Fallback to ResContract CLI
                result = await rescontract_client.get_transaction(transaction_id)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "postTransaction":
            data = arguments["data"]
            result = await graphql_client.post_transaction(data)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "updateTransaction":
            transaction_id = arguments["transactionId"]
            data = arguments["data"]
            result = await graphql_client.update_transaction(transaction_id, data)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get":
            key = arguments["key"]
            result = await graphql_client.get_key_value(key)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "set":
            key = arguments["key"]
            value = arguments["value"]
            result = await graphql_client.set_key_value(key, value)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "getContractState":
            contract_address = arguments["contractAddress"]
            result = await rescontract_client.get_contract_state(contract_address)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        error_message = f"Error executing tool '{name}': {str(e)}"
        error_details = {
            "error": type(e).__name__,
            "message": error_message,
            "tool": name,
            "arguments": arguments
        }
        return [TextContent(
            type="text",
            text=json.dumps(error_details, indent=2)
        )]


async def main():
    """Main entry point for the MCP server."""
    # Run the server using stdio transport
    # The stdio_server context manager returns (read_stream, write_stream)
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

