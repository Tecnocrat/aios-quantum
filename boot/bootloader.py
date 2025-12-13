#!/usr/bin/env python3
"""
=============================================================================
AIOS QUANTUM BOOTLOADER
=============================================================================
Clean startup sequence for the quantum visualizer stack.

Features:
- Environment validation
- Dependency checks
- Service initialization
- Health monitoring
- Graceful shutdown
=============================================================================
"""

import os
import sys
import time
import json
import signal
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from enum import Enum

# =============================================================================
# CONFIGURATION
# =============================================================================

class ServiceState(Enum):
    """Service lifecycle states."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    FAILED = "failed"

@dataclass
class ServiceConfig:
    """Configuration for a managed service."""
    name: str
    command: List[str]
    working_dir: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)
    health_check: Optional[str] = None
    health_interval: int = 30
    depends_on: List[str] = field(default_factory=list)
    required: bool = True

@dataclass
class BootConfig:
    """Bootloader configuration."""
    # Paths
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    web_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "web")
    logs_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "logs")
    
    # Timeouts
    startup_timeout: int = 60
    shutdown_timeout: int = 30
    health_check_interval: int = 30
    
    # Features
    enable_metrics: bool = True
    enable_api: bool = False
    dev_mode: bool = False

# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging(config: BootConfig) -> logging.Logger:
    """Configure structured logging."""
    config.logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = config.logs_dir / f"bootloader_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColorFormatter())
    console_handler.setLevel(logging.INFO)
    
    # Configure root logger
    logger = logging.getLogger("bootloader")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

class ColorFormatter(logging.Formatter):
    """Colored console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        prefix = f"{color}{self.BOLD}[{record.levelname}]{self.RESET}"
        return f"{prefix} {record.getMessage()}"

# =============================================================================
# ENVIRONMENT VALIDATION
# =============================================================================

@dataclass
class ValidationResult:
    """Result of environment validation."""
    valid: bool
    checks: Dict[str, bool]
    errors: List[str]
    warnings: List[str]

def validate_environment(config: BootConfig, logger: logging.Logger) -> ValidationResult:
    """Validate environment before startup."""
    checks = {}
    errors = []
    warnings = []
    
    logger.info("🔍 Validating environment...")
    
    # Check Node.js
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True, text=True, timeout=10
        )
        version = result.stdout.strip()
        checks["nodejs"] = result.returncode == 0
        if checks["nodejs"]:
            logger.info(f"  ✅ Node.js: {version}")
        else:
            errors.append("Node.js not found")
            logger.error("  ❌ Node.js not found")
    except Exception as e:
        checks["nodejs"] = False
        errors.append(f"Node.js check failed: {e}")
        logger.error(f"  ❌ Node.js check failed: {e}")
    
    # Check npm
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True, text=True, timeout=10
        )
        checks["npm"] = result.returncode == 0
        if checks["npm"]:
            logger.info(f"  ✅ npm: v{result.stdout.strip()}")
    except Exception:
        checks["npm"] = False
        errors.append("npm not found")
    
    # Check Python
    try:
        result = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True, text=True, timeout=10
        )
        checks["python"] = result.returncode == 0
        if checks["python"]:
            logger.info(f"  ✅ Python: {result.stdout.strip()}")
    except Exception:
        checks["python"] = False
        errors.append("Python check failed")
    
    # Check web directory
    checks["web_dir"] = config.web_dir.exists()
    if checks["web_dir"]:
        logger.info(f"  ✅ Web directory: {config.web_dir}")
    else:
        errors.append(f"Web directory not found: {config.web_dir}")
        logger.error(f"  ❌ Web directory not found: {config.web_dir}")
    
    # Check package.json
    package_json = config.web_dir / "package.json"
    checks["package_json"] = package_json.exists()
    if checks["package_json"]:
        logger.info("  ✅ package.json found")
    else:
        errors.append("package.json not found")
    
    # Check node_modules
    node_modules = config.web_dir / "node_modules"
    checks["node_modules"] = node_modules.exists()
    if not checks["node_modules"]:
        warnings.append("node_modules not found - will run npm install")
        logger.warning("  ⚠️  node_modules not found - will install")
    else:
        logger.info("  ✅ node_modules found")
    
    # Check quantum experiments data
    experiments_file = config.web_dir / "public" / "quantum_experiments.json"
    checks["experiments_data"] = experiments_file.exists()
    if checks["experiments_data"]:
        logger.info("  ✅ Quantum experiments data found")
    else:
        warnings.append("quantum_experiments.json not found - visualization may be empty")
        logger.warning("  ⚠️  quantum_experiments.json not found")
    
    # Overall validation
    required_checks = ["nodejs", "npm", "python", "web_dir", "package_json"]
    valid = all(checks.get(c, False) for c in required_checks)
    
    return ValidationResult(
        valid=valid,
        checks=checks,
        errors=errors,
        warnings=warnings
    )

# =============================================================================
# SERVICE MANAGER
# =============================================================================

class ServiceManager:
    """Manages service lifecycle."""
    
    def __init__(self, config: BootConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.processes: Dict[str, subprocess.Popen] = {}
        self.states: Dict[str, ServiceState] = {}
        self._shutdown_requested = False
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"\n🛑 Received signal {signum}, initiating shutdown...")
        self._shutdown_requested = True
        self.shutdown_all()
    
    def start_service(self, service: ServiceConfig) -> bool:
        """Start a service."""
        self.logger.info(f"🚀 Starting {service.name}...")
        self.states[service.name] = ServiceState.STARTING
        
        try:
            # Prepare environment
            env = os.environ.copy()
            env.update(service.env)
            
            # Determine working directory
            cwd = service.working_dir or str(self.config.project_root)
            
            # Start process
            process = subprocess.Popen(
                service.command,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            self.processes[service.name] = process
            
            # Wait a moment and check if it started
            time.sleep(2)
            
            if process.poll() is not None:
                # Process exited immediately
                stdout, _ = process.communicate()
                self.logger.error(f"  ❌ {service.name} failed to start")
                self.logger.error(f"     Output: {stdout[:500] if stdout else 'none'}")
                self.states[service.name] = ServiceState.FAILED
                return False
            
            self.states[service.name] = ServiceState.RUNNING
            self.logger.info(f"  ✅ {service.name} started (PID: {process.pid})")
            return True
            
        except Exception as e:
            self.logger.error(f"  ❌ Failed to start {service.name}: {e}")
            self.states[service.name] = ServiceState.FAILED
            return False
    
    def stop_service(self, name: str) -> bool:
        """Stop a service gracefully."""
        if name not in self.processes:
            return True
        
        self.logger.info(f"🛑 Stopping {name}...")
        self.states[name] = ServiceState.STOPPING
        
        process = self.processes[name]
        
        try:
            # Try graceful termination
            process.terminate()
            try:
                process.wait(timeout=self.config.shutdown_timeout)
            except subprocess.TimeoutExpired:
                self.logger.warning(f"  ⚠️  {name} didn't stop gracefully, killing...")
                process.kill()
                process.wait(timeout=5)
            
            self.states[name] = ServiceState.STOPPED
            self.logger.info(f"  ✅ {name} stopped")
            del self.processes[name]
            return True
            
        except Exception as e:
            self.logger.error(f"  ❌ Failed to stop {name}: {e}")
            return False
    
    def shutdown_all(self):
        """Shutdown all services."""
        self.logger.info("🔄 Shutting down all services...")
        
        for name in list(self.processes.keys()):
            self.stop_service(name)
        
        self.logger.info("✅ All services stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all services."""
        status = {}
        for name, process in self.processes.items():
            status[name] = {
                "state": self.states.get(name, ServiceState.STOPPED).value,
                "pid": process.pid if process.poll() is None else None,
                "running": process.poll() is None
            }
        return status

# =============================================================================
# BOOTLOADER
# =============================================================================

class Bootloader:
    """Main bootloader orchestrator."""
    
    def __init__(self, config: Optional[BootConfig] = None):
        self.config = config or BootConfig()
        self.logger = setup_logging(self.config)
        self.service_manager = ServiceManager(self.config, self.logger)
        self.start_time = datetime.now()
    
    def print_banner(self):
        """Print startup banner."""
        banner = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║     █████╗ ██╗ ██████╗ ███████╗     ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗  ║
║    ██╔══██╗██║██╔═══██╗██╔════╝    ██╔═══██╗██║   ██║██╔══██╗████╗  ██║  ║
║    ███████║██║██║   ██║███████╗    ██║   ██║██║   ██║███████║██╔██╗ ██║  ║
║    ██╔══██║██║██║   ██║╚════██║    ██║▄▄ ██║██║   ██║██╔══██║██║╚██╗██║  ║
║    ██║  ██║██║╚██████╔╝███████║    ╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║  ║
║    ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚══════╝     ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝  ║
║                                                                           ║
║                    🌌 QUANTUM VISUALIZER BOOTLOADER 🌌                    ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  📁 Project: {self.config.project_root}")
        print(f"  🐍 Python: {sys.version.split()[0]}")
        print()
    
    def install_dependencies(self) -> bool:
        """Install npm dependencies if needed."""
        node_modules = self.config.web_dir / "node_modules"
        
        if node_modules.exists():
            return True
        
        self.logger.info("📦 Installing npm dependencies...")
        
        try:
            result = subprocess.run(
                ["npm", "install"],
                cwd=str(self.config.web_dir),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.logger.info("  ✅ Dependencies installed")
                return True
            else:
                self.logger.error(f"  ❌ npm install failed: {result.stderr[:500]}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("  ❌ npm install timed out")
            return False
        except Exception as e:
            self.logger.error(f"  ❌ npm install failed: {e}")
            return False
    
    def start_dev_server(self) -> bool:
        """Start the Next.js development server."""
        service = ServiceConfig(
            name="nextjs-dev",
            command=["npm", "run", "dev"],
            working_dir=str(self.config.web_dir),
            env={"NODE_ENV": "development"},
            health_check="http://localhost:3000/api/health",
            required=True
        )
        
        return self.service_manager.start_service(service)
    
    def start_production_server(self) -> bool:
        """Build and start production server."""
        self.logger.info("🏗️  Building for production...")
        
        # Build
        try:
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=str(self.config.web_dir),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                self.logger.error(f"  ❌ Build failed: {result.stderr[:500]}")
                return False
            
            self.logger.info("  ✅ Build complete")
            
        except Exception as e:
            self.logger.error(f"  ❌ Build failed: {e}")
            return False
        
        # Start production server
        service = ServiceConfig(
            name="nextjs-prod",
            command=["npm", "run", "start"],
            working_dir=str(self.config.web_dir),
            env={"NODE_ENV": "production"},
            required=True
        )
        
        return self.service_manager.start_service(service)
    
    def write_metadata(self):
        """Write startup metadata."""
        metadata = {
            "boot_time": self.start_time.isoformat(),
            "config": {
                "project_root": str(self.config.project_root),
                "web_dir": str(self.config.web_dir),
                "dev_mode": self.config.dev_mode
            },
            "services": self.service_manager.get_status(),
            "python_version": sys.version,
            "pid": os.getpid()
        }
        
        metadata_file = self.config.logs_dir / "bootloader_state.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.debug(f"Metadata written to {metadata_file}")
    
    def run(self, dev_mode: bool = True) -> int:
        """Run the bootloader."""
        self.config.dev_mode = dev_mode
        self.print_banner()
        
        # Validate environment
        validation = validate_environment(self.config, self.logger)
        
        if not validation.valid:
            self.logger.error("❌ Environment validation failed!")
            for error in validation.errors:
                self.logger.error(f"   • {error}")
            return 1
        
        if validation.warnings:
            for warning in validation.warnings:
                self.logger.warning(f"   • {warning}")
        
        # Install dependencies if needed
        if not self.install_dependencies():
            return 1
        
        # Start server
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info("STARTING SERVICES")
        self.logger.info("=" * 60)
        self.logger.info("")
        
        if dev_mode:
            if not self.start_dev_server():
                return 1
        else:
            if not self.start_production_server():
                return 1
        
        # Write metadata
        self.write_metadata()
        
        # Print success message
        print()
        print("╔═══════════════════════════════════════════════════════════════╗")
        print("║  🎉 QUANTUM VISUALIZER IS RUNNING                             ║")
        print("║                                                               ║")
        print("║  📍 Local:    http://localhost:3000                           ║")
        print("║  📍 Network:  http://<your-ip>:3000                           ║")
        print("║                                                               ║")
        print("║  🌌 Visualizations:                                           ║")
        print("║     • Hypersphere:   /hypersphere                             ║")
        print("║     • Experiments:   /hypersphere/experiments                 ║")
        print("║     • All Modes:     /hypersphere/visualizations              ║")
        print("║                                                               ║")
        print("║  Press Ctrl+C to stop                                         ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        print()
        
        # Keep running until shutdown
        try:
            while not self.service_manager._shutdown_requested:
                # Check service health
                status = self.service_manager.get_status()
                for name, info in status.items():
                    if not info["running"]:
                        self.logger.error(f"Service {name} has stopped unexpectedly!")
                        return 1
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            pass
        
        return 0

# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AIOS Quantum Visualizer Bootloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bootloader.py                 # Start dev server
  python bootloader.py --prod          # Build and start production
  python bootloader.py --validate      # Only validate environment
        """
    )
    
    parser.add_argument(
        "--prod", "--production",
        action="store_true",
        help="Run in production mode"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Only validate environment, don't start services"
    )
    
    parser.add_argument(
        "--web-dir",
        type=Path,
        help="Path to web directory"
    )
    
    args = parser.parse_args()
    
    # Build config
    config = BootConfig()
    if args.web_dir:
        config.web_dir = args.web_dir
    
    bootloader = Bootloader(config)
    
    if args.validate:
        bootloader.print_banner()
        validation = validate_environment(config, bootloader.logger)
        
        print("\n" + "=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)
        
        for check, passed in validation.checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
        
        print()
        if validation.valid:
            print("✅ Environment is valid")
            return 0
        else:
            print("❌ Environment validation failed")
            return 1
    
    return bootloader.run(dev_mode=not args.prod)


if __name__ == "__main__":
    sys.exit(main())
