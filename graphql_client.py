"""GraphQL client for ResilientDB operations."""
import httpx
from typing import Dict, Any, Optional
from config import Config
import json


class GraphQLClient:
    """Client for executing GraphQL queries and mutations on ResilientDB."""
    
    def __init__(self, url: str = None, api_key: Optional[str] = None):
        self.url = url or Config.GRAPHQL_URL
        self.api_key = api_key or Config.API_KEY
        self.timeout = Config.REQUEST_TIMEOUT
        
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for requests."""
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query.
        
        Args:
            query: GraphQL query string
            variables: Optional variables for the query
            
        Returns:
            Response data from GraphQL server
        """
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.url,
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            result = response.json()
            
            if "errors" in result:
                error_msg = json.dumps(result["errors"], indent=2)
                raise Exception(f"GraphQL errors: {error_msg}")
            
            return result.get("data", {})
    
    async def create_account(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new account in ResilientDB."""
        mutation = """
        mutation CreateAccount($accountId: String) {
            createAccount(accountId: $accountId) {
                accountId
                publicKey
                createdAt
            }
        }
        """
        variables = {}
        if account_id:
            variables["accountId"] = account_id
            
        return await self.execute_query(mutation, variables)
    
    async def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction by ID."""
        query = """
        query GetTransaction($transactionId: String!) {
            transaction(transactionId: $transactionId) {
                id
                timestamp
                status
                data
                blockNumber
            }
        }
        """
        return await self.execute_query(query, {"transactionId": transaction_id})
    
    async def post_transaction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Post a new transaction."""
        mutation = """
        mutation PostTransaction($data: JSON!) {
            postTransaction(data: $data) {
                transactionId
                status
                timestamp
            }
        }
        """
        return await self.execute_query(mutation, {"data": data})
    
    async def update_transaction(self, transaction_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing transaction."""
        mutation = """
        mutation UpdateTransaction($transactionId: String!, $data: JSON!) {
            updateTransaction(transactionId: $transactionId, data: $data) {
                transactionId
                status
                updatedAt
            }
        }
        """
        return await self.execute_query(
            mutation, 
            {"transactionId": transaction_id, "data": data}
        )
    
    async def get_key_value(self, key: str) -> Dict[str, Any]:
        """Query key-value store."""
        query = """
        query GetKeyValue($key: String!) {
            keyValue(key: $key) {
                key
                value
                timestamp
            }
        }
        """
        return await self.execute_query(query, {"key": key})
    
    async def set_key_value(self, key: str, value: Any) -> Dict[str, Any]:
        """Set key-value pair."""
        # Convert value to string if it's not already
        if not isinstance(value, str):
            value = json.dumps(value)
        
        mutation = """
        mutation SetKeyValue($key: String!, $value: String!) {
            setKeyValue(key: $key, value: $value) {
                key
                value
                timestamp
            }
        }
        """
        return await self.execute_query(mutation, {"key": key, "value": value})

