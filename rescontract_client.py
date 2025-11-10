"""ResContract CLI client for smart contract operations."""
import subprocess
import json
import os
from typing import Dict, Any, Optional, List
from config import Config
import asyncio
from pathlib import Path


class ResContractClient:
    """Client for executing ResContract CLI commands."""
    
    def __init__(self, cli_path: str = None):
        self.cli_path = cli_path or Config.RESCONTRACT_CLI_PATH
        
    async def _execute_command(self, command: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a ResContract CLI command.
        
        Args:
            command: Command and arguments as a list
            cwd: Working directory for the command
            
        Returns:
            Command output as dictionary
        """
        full_command = [self.cli_path] + command
        
        try:
            process = await asyncio.create_subprocess_exec(
                *full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise Exception(f"ResContract CLI error: {error_msg}")
            
            output = stdout.decode().strip()
            
            # Try to parse as JSON, otherwise return as string
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return {"output": output, "raw": True}
                
        except FileNotFoundError:
            raise Exception(
                f"ResContract CLI not found at '{self.cli_path}'. "
                "Please ensure it's installed and in your PATH, or set RESCONTRACT_CLI_PATH."
            )
    
    async def compile_contract(self, contract_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Compile a smart contract."""
        contract_file = Path(contract_path)
        if not contract_file.exists():
            raise FileNotFoundError(f"Contract file not found: {contract_path}")
        
        command = ["compile", str(contract_file)]
        if output_dir:
            command.extend(["-o", output_dir])
        
        return await self._execute_command(command, cwd=contract_file.parent)
    
    async def deploy_contract(
        self, 
        contract_path: str,
        account_id: Optional[str] = None,
        constructor_args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Deploy a smart contract."""
        command = ["deploy", contract_path]
        
        if account_id:
            command.extend(["--account", account_id])
        
        if constructor_args:
            command.extend(["--args"] + constructor_args)
        
        return await self._execute_command(command)
    
    async def execute_contract(
        self,
        contract_address: str,
        method_name: str,
        method_args: Optional[List[str]] = None,
        account_id: Optional[str] = None,
        transaction_type: str = "call"  # "call" or "send"
    ) -> Dict[str, Any]:
        """Execute a contract method."""
        command = [transaction_type, contract_address, method_name]
        
        if account_id:
            command.extend(["--account", account_id])
        
        if method_args:
            command.extend(["--args"] + method_args)
        
        return await self._execute_command(command)
    
    async def get_contract_state(self, contract_address: str) -> Dict[str, Any]:
        """Get the current state of a contract."""
        command = ["state", contract_address]
        return await self._execute_command(command)
    
    async def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction details."""
        command = ["transaction", transaction_id]
        return await self._execute_command(command)

