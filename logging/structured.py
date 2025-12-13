#!/usr/bin/env python3
"""
=============================================================================
AIOS QUANTUM STRUCTURED LOGGING
=============================================================================
Production-ready logging utilities with:
- Structured JSON output
- Correlation IDs
- Context propagation
- Performance metrics
- Multiple output handlers
=============================================================================
"""

import os
import sys
import json
import time
import uuid
import logging
import threading
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List, Callable
from contextlib import contextmanager
from functools import wraps

# =============================================================================
# CORRELATION CONTEXT
# =============================================================================

class CorrelationContext:
    """Thread-local correlation context for request tracing."""
    
    _local = threading.local()
    
    @classmethod
    def get_id(cls) -> str:
        """Get current correlation ID."""
        if not hasattr(cls._local, 'correlation_id'):
            cls._local.correlation_id = str(uuid.uuid4())[:8]
        return cls._local.correlation_id
    
    @classmethod
    def set_id(cls, correlation_id: str):
        """Set correlation ID."""
        cls._local.correlation_id = correlation_id
    
    @classmethod
    def new_id(cls) -> str:
        """Generate and set new correlation ID."""
        correlation_id = str(uuid.uuid4())[:8]
        cls._local.correlation_id = correlation_id
        return correlation_id
    
    @classmethod
    @contextmanager
    def scope(cls, correlation_id: Optional[str] = None):
        """Context manager for correlation scope."""
        old_id = getattr(cls._local, 'correlation_id', None)
        cls._local.correlation_id = correlation_id or str(uuid.uuid4())[:8]
        try:
            yield cls._local.correlation_id
        finally:
            if old_id:
                cls._local.correlation_id = old_id
            elif hasattr(cls._local, 'correlation_id'):
                delattr(cls._local, 'correlation_id')

# =============================================================================
# STRUCTURED LOG RECORD
# =============================================================================

@dataclass
class StructuredLogRecord:
    """Structured log entry."""
    timestamp: str
    level: str
    logger: str
    message: str
    correlation_id: str
    extra: Dict[str, Any] = field(default_factory=dict)
    exception: Optional[str] = None
    
    # Performance metrics
    duration_ms: Optional[float] = None
    
    # Context
    module: Optional[str] = None
    function: Optional[str] = None
    line: Optional[int] = None
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        data = {k: v for k, v in asdict(self).items() if v is not None}
        return json.dumps(data, default=str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}

# =============================================================================
# JSON FORMATTER
# =============================================================================

class StructuredJsonFormatter(logging.Formatter):
    """Format log records as JSON."""
    
    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """Format record as JSON."""
        
        # Extract exception info
        exception = None
        if record.exc_info:
            exception = self.formatException(record.exc_info)
        
        # Build extra fields
        extra = {}
        if self.include_extra:
            standard_attrs = {
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'pathname', 'process', 'processName', 'relativeCreated',
                'stack_info', 'exc_info', 'exc_text', 'thread', 'threadName',
                'message', 'asctime'
            }
            extra = {
                k: v for k, v in record.__dict__.items()
                if k not in standard_attrs and not k.startswith('_')
            }
        
        # Create structured record
        structured = StructuredLogRecord(
            timestamp=datetime.fromtimestamp(record.created).isoformat(),
            level=record.levelname,
            logger=record.name,
            message=record.getMessage(),
            correlation_id=CorrelationContext.get_id(),
            extra=extra,
            exception=exception,
            module=record.module,
            function=record.funcName,
            line=record.lineno,
            duration_ms=getattr(record, 'duration_ms', None)
        )
        
        return structured.to_json()

# =============================================================================
# CONSOLE FORMATTER
# =============================================================================

class ColoredConsoleFormatter(logging.Formatter):
    """Human-readable colored console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format with colors."""
        color = self.COLORS.get(record.levelname, '')
        correlation_id = CorrelationContext.get_id()
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S.%f')[:-3]
        
        # Build message
        parts = [
            f"{self.DIM}{timestamp}{self.RESET}",
            f"{color}{self.BOLD}[{record.levelname:8}]{self.RESET}",
            f"{self.DIM}[{correlation_id}]{self.RESET}",
            record.getMessage()
        ]
        
        # Add duration if present
        if hasattr(record, 'duration_ms'):
            parts.append(f"{self.DIM}({record.duration_ms:.2f}ms){self.RESET}")
        
        message = " ".join(parts)
        
        # Add exception
        if record.exc_info:
            message += "\n" + self.formatException(record.exc_info)
        
        return message

# =============================================================================
# QUANTUM METRICS LOGGER
# =============================================================================

class QuantumMetricsLogger:
    """Specialized logger for quantum experiment metrics."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_circuit_execution(
        self,
        circuit_name: str,
        backend: str,
        qubits: int,
        depth: int,
        shots: int,
        execution_time_ms: float,
        coherence: Optional[float] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Log quantum circuit execution."""
        self.logger.info(
            f"Circuit executed: {circuit_name}",
            extra={
                "event_type": "circuit_execution",
                "circuit_name": circuit_name,
                "backend": backend,
                "qubits": qubits,
                "depth": depth,
                "shots": shots,
                "duration_ms": execution_time_ms,
                "coherence": coherence,
                **(extra or {})
            }
        )
    
    def log_job_submission(
        self,
        job_id: str,
        backend: str,
        circuit_name: str,
        qubits: int
    ):
        """Log job submission."""
        self.logger.info(
            f"Job submitted: {job_id}",
            extra={
                "event_type": "job_submission",
                "job_id": job_id,
                "backend": backend,
                "circuit_name": circuit_name,
                "qubits": qubits
            }
        )
    
    def log_job_completion(
        self,
        job_id: str,
        status: str,
        execution_time_ms: float,
        result_summary: Optional[Dict[str, Any]] = None
    ):
        """Log job completion."""
        self.logger.info(
            f"Job completed: {job_id} ({status})",
            extra={
                "event_type": "job_completion",
                "job_id": job_id,
                "status": status,
                "duration_ms": execution_time_ms,
                "result": result_summary
            }
        )
    
    def log_visualization_render(
        self,
        mode: str,
        frame_time_ms: float,
        particles: int,
        fps: float
    ):
        """Log visualization render metrics."""
        self.logger.debug(
            f"Render frame: {mode}",
            extra={
                "event_type": "render_frame",
                "mode": mode,
                "frame_time_ms": frame_time_ms,
                "particles": particles,
                "fps": fps
            }
        )

# =============================================================================
# PERFORMANCE TIMING
# =============================================================================

@contextmanager
def timed_operation(logger: logging.Logger, operation: str, **extra):
    """Context manager for timing operations."""
    start = time.perf_counter()
    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            f"{operation} completed",
            extra={"duration_ms": duration_ms, **extra}
        )

def timed(logger: logging.Logger = None):
    """Decorator for timing functions."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = logging.getLogger(func.__module__)
            
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000
                logger.debug(
                    f"{func.__name__} completed",
                    extra={"duration_ms": duration_ms}
                )
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                logger.exception(
                    f"{func.__name__} failed",
                    extra={"duration_ms": duration_ms}
                )
                raise
        return wrapper
    return decorator

# =============================================================================
# LOGGER FACTORY
# =============================================================================

class LoggerFactory:
    """Factory for creating configured loggers."""
    
    _loggers: Dict[str, logging.Logger] = {}
    _configured = False
    _log_dir: Optional[Path] = None
    
    @classmethod
    def configure(
        cls,
        log_dir: Optional[Path] = None,
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        json_output: bool = True
    ):
        """Configure logging system."""
        if cls._configured:
            return
        
        # Set log directory
        cls._log_dir = log_dir or Path("logs")
        cls._log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create root logger configuration
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(ColoredConsoleFormatter())
        root.addHandler(console_handler)
        
        # File handler (JSON)
        if json_output:
            log_file = cls._log_dir / f"quantum_{datetime.now().strftime('%Y%m%d')}.jsonl"
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(file_level)
            file_handler.setFormatter(StructuredJsonFormatter())
            root.addHandler(file_handler)
        
        cls._configured = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get or create a named logger."""
        if not cls._configured:
            cls.configure()
        
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        
        return cls._loggers[name]
    
    @classmethod
    def get_quantum_logger(cls, name: str = "quantum") -> QuantumMetricsLogger:
        """Get quantum metrics logger."""
        return QuantumMetricsLogger(cls.get_logger(name))

# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger."""
    return LoggerFactory.get_logger(name)

def get_quantum_logger() -> QuantumMetricsLogger:
    """Get quantum metrics logger."""
    return LoggerFactory.get_quantum_logger()

def configure_logging(**kwargs):
    """Configure the logging system."""
    LoggerFactory.configure(**kwargs)

# =============================================================================
# LOG AGGREGATOR
# =============================================================================

class LogAggregator:
    """Aggregate and analyze log entries."""
    
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
    
    def read_logs(self, date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Read log entries from JSONL files."""
        if date is None:
            date = datetime.now()
        
        log_file = self.log_dir / f"quantum_{date.strftime('%Y%m%d')}.jsonl"
        
        if not log_file.exists():
            return []
        
        entries = []
        with open(log_file) as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return entries
    
    def get_statistics(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get statistics from logs."""
        entries = self.read_logs(date)
        
        if not entries:
            return {"total": 0}
        
        # Count by level
        by_level = {}
        for entry in entries:
            level = entry.get("level", "UNKNOWN")
            by_level[level] = by_level.get(level, 0) + 1
        
        # Count by event type
        by_event = {}
        for entry in entries:
            event_type = entry.get("extra", {}).get("event_type", "general")
            by_event[event_type] = by_event.get(event_type, 0) + 1
        
        # Calculate average durations
        durations = [
            e.get("duration_ms") for e in entries
            if e.get("duration_ms") is not None
        ]
        
        return {
            "total": len(entries),
            "by_level": by_level,
            "by_event": by_event,
            "avg_duration_ms": sum(durations) / len(durations) if durations else None,
            "errors": by_level.get("ERROR", 0) + by_level.get("CRITICAL", 0)
        }

# =============================================================================
# CLI
# =============================================================================

def main():
    """CLI for log utilities."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AIOS Quantum Logging Utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show log statistics")
    stats_parser.add_argument("--log-dir", type=Path, default=Path("logs"))
    stats_parser.add_argument("--date", help="Date (YYYY-MM-DD)")
    
    # Tail command
    tail_parser = subparsers.add_parser("tail", help="Tail log file")
    tail_parser.add_argument("--log-dir", type=Path, default=Path("logs"))
    tail_parser.add_argument("-n", type=int, default=20, help="Number of lines")
    
    args = parser.parse_args()
    
    if args.command == "stats":
        date = datetime.strptime(args.date, "%Y-%m-%d") if args.date else None
        aggregator = LogAggregator(args.log_dir)
        stats = aggregator.get_statistics(date)
        print(json.dumps(stats, indent=2))
    
    elif args.command == "tail":
        aggregator = LogAggregator(args.log_dir)
        entries = aggregator.read_logs()[-args.n:]
        for entry in entries:
            print(json.dumps(entry))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
