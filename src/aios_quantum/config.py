"""
Configuration management for IBM Quantum connection.
"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class QuantumConfig:
    """Configuration for IBM Quantum Platform connection."""
    
    token: str
    instance: str = "open-instance"
    channel: str = "ibm_quantum_platform"
    
    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "QuantumConfig":
        """
        Load configuration from environment variables.
        
        Args:
            env_file: Optional path to .env file
            
        Returns:
            QuantumConfig instance
            
        Raises:
            ValueError: If IBM_QUANTUM_TOKEN is not set
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        token = os.getenv("IBM_QUANTUM_TOKEN")
        if not token:
            raise ValueError(
                "IBM_QUANTUM_TOKEN environment variable is required. "
                "Get your token from https://quantum.cloud.ibm.com/"
            )
        
        return cls(
            token=token,
            instance=os.getenv("IBM_QUANTUM_INSTANCE", "ibm-q/open/main"),
            channel=os.getenv("IBM_QUANTUM_CHANNEL", "ibm_cloud"),
        )
    
    def __repr__(self) -> str:
        """Safe repr that doesn't expose the token."""
        return (
            f"QuantumConfig(token='***', "
            f"instance='{self.instance}', "
            f"channel='{self.channel}')"
        )
