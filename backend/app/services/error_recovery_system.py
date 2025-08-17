"""
Error Recovery System

Comprehensive error handling and recovery mechanisms for graceful degradation
when components fail or encounter issues.
"""

import asyncio
import json
import time
import traceback
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager

import structlog

logger = structlog.get_logger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"           # Minor issues, system continues normally
    MEDIUM = "medium"     # Some functionality affected, fallbacks used
    HIGH = "high"         # Major functionality affected, significant degradation
    CRITICAL = "critical" # System-wide failure, emergency fallbacks


class RecoveryStrategy(Enum):
    """Recovery strategy types."""
    RETRY = "retry"                    # Retry the operation
    FALLBACK = "fallback"             # Use fallback mechanism
    SKIP = "skip"                     # Skip the operation
    ALTERNATIVE = "alternative"       # Use alternative approach
    GRACEFUL_DEGRADATION = "graceful" # Provide limited functionality
    EMERGENCY_STOP = "emergency"      # Stop execution safely


@dataclass
class ErrorContext:
    """Context information about an error."""
    error_id: str
    error_type: str
    error_message: str
    stack_trace: str
    component: str
    operation: str
    timestamp: float
    severity: ErrorSeverity
    metadata: Dict[str, Any] = field(default_factory=dict)
    recovery_attempts: int = 0
    max_recovery_attempts: int = 3


@dataclass
class RecoveryAction:
    """Action to take for error recovery."""
    action_id: str
    strategy: RecoveryStrategy
    handler: Callable
    condition: Optional[Callable] = None
    priority: int = 1
    max_attempts: int = 3
    timeout: float = 30.0
    description: str = ""


class ErrorRecoverySystem:
    """
    Comprehensive error recovery system that provides:
    - Automatic error detection and classification
    - Multiple recovery strategies
    - Graceful degradation mechanisms
    - Fallback systems
    - Error reporting and monitoring
    """
    
    def __init__(self):
        self.error_handlers: Dict[str, List[RecoveryAction]] = {}
        self.fallback_providers: Dict[str, Callable] = {}
        self.error_history: List[ErrorContext] = []
        self.recovery_stats: Dict[str, Dict[str, Any]] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Default configuration
        self.config = {
            'max_error_history': 1000,
            'circuit_breaker_threshold': 5,
            'circuit_breaker_timeout': 300,  # 5 minutes
            'default_retry_attempts': 3,
            'default_timeout': 30.0
        }
        
        # Initialize default handlers
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default error handlers for common scenarios."""
        
        # AI Provider failures
        self.register_handler(
            'ai_provider_error',
            RecoveryAction(
                action_id='switch_ai_provider',
                strategy=RecoveryStrategy.ALTERNATIVE,
                handler=self._switch_ai_provider,
                priority=1,
                description='Switch to backup AI provider'
            )
        )
        
        # Network/API failures
        self.register_handler(
            'network_error',
            RecoveryAction(
                action_id='retry_with_backoff',
                strategy=RecoveryStrategy.RETRY,
                handler=self._retry_with_backoff,
                priority=1,
                max_attempts=3,
                description='Retry with exponential backoff'
            )
        )
        
        # Parsing/Format failures
        self.register_handler(
            'parsing_error',
            RecoveryAction(
                action_id='fallback_parsing',
                strategy=RecoveryStrategy.FALLBACK,
                handler=self._fallback_parsing,
                priority=1,
                description='Use fallback parsing method'
            )
        )
        
        # Rendering failures
        self.register_handler(
            'rendering_error',
            RecoveryAction(
                action_id='graceful_rendering',
                strategy=RecoveryStrategy.GRACEFUL_DEGRADATION,
                handler=self._graceful_rendering_fallback,
                priority=1,
                description='Render with reduced functionality'
            )
        )
        
        # Tool execution failures
        self.register_handler(
            'tool_error',
            RecoveryAction(
                action_id='alternative_tool',
                strategy=RecoveryStrategy.ALTERNATIVE,
                handler=self._try_alternative_tool,
                priority=1,
                description='Try alternative tool or method'
            )
        )
    
    def register_handler(self, error_type: str, action: RecoveryAction):
        """Register an error recovery handler."""
        if error_type not in self.error_handlers:
            self.error_handlers[error_type] = []
        
        self.error_handlers[error_type].append(action)
        
        # Sort by priority (higher priority first)
        self.error_handlers[error_type].sort(key=lambda x: x.priority, reverse=True)
        
        logger.info(f"Error handler registered", error_type=error_type, action_id=action.action_id)
    
    def register_fallback_provider(self, component: str, provider: Callable):
        """Register a fallback provider for a component."""
        self.fallback_providers[component] = provider
        logger.info(f"Fallback provider registered", component=component)
    
    @asynccontextmanager
    async def error_boundary(
        self,
        component: str,
        operation: str,
        error_types: Optional[List[str]] = None,
        fallback_value: Any = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM
    ):
        """
        Context manager that provides error boundary with automatic recovery.
        
        Usage:
            async with error_recovery.error_boundary('ai_provider', 'generate_completion'):
                result = await ai_provider.generate(prompt)
        """
        error_context = None
        
        try:
            yield
            
        except Exception as e:
            # Create error context
            error_context = ErrorContext(
                error_id=f"{component}_{operation}_{int(time.time())}",
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc(),
                component=component,
                operation=operation,
                timestamp=time.time(),
                severity=severity,
                metadata={
                    'error_types': error_types,
                    'fallback_value': fallback_value
                }
            )
            
            # Add to error history
            self.error_history.append(error_context)
            self._cleanup_error_history()
            
            # Check circuit breaker
            if self._should_circuit_break(component, operation):
                logger.warning(f"Circuit breaker activated", component=component, operation=operation)
                if fallback_value is not None:
                    return fallback_value
                raise
            
            # Attempt recovery
            recovery_result = await self._attempt_recovery(error_context)
            
            if not recovery_result['success']:
                # Recovery failed, use fallback or re-raise
                if fallback_value is not None:
                    logger.info(f"Using fallback value", component=component, operation=operation)
                    return fallback_value
                
                # Try component fallback provider
                if component in self.fallback_providers:
                    try:
                        fallback_result = await self.fallback_providers[component](error_context)
                        logger.info(f"Fallback provider succeeded", component=component)
                        return fallback_result
                    except Exception as fallback_error:
                        logger.error(f"Fallback provider failed", component=component, error=str(fallback_error))
                
                # All recovery attempts failed
                logger.error(f"All recovery attempts failed", error_id=error_context.error_id)
                raise
            
            return recovery_result['result']
    
    async def _attempt_recovery(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Attempt to recover from an error using registered handlers."""
        
        # Find applicable handlers
        handlers = self._find_applicable_handlers(error_context)
        
        if not handlers:
            logger.warning(f"No recovery handlers found", error_type=error_context.error_type)
            return {'success': False, 'reason': 'No handlers found'}
        
        # Try each handler in priority order
        for handler in handlers:
            if error_context.recovery_attempts >= handler.max_attempts:
                continue
            
            try:
                logger.info(
                    f"Attempting recovery",
                    error_id=error_context.error_id,
                    handler=handler.action_id,
                    attempt=error_context.recovery_attempts + 1
                )
                
                # Check condition if provided
                if handler.condition and not await handler.condition(error_context):
                    continue
                
                # Execute recovery handler with timeout
                result = await asyncio.wait_for(
                    handler.handler(error_context),
                    timeout=handler.timeout
                )
                
                error_context.recovery_attempts += 1
                
                # Update recovery stats
                self._update_recovery_stats(handler.action_id, True)
                
                logger.info(
                    f"Recovery successful",
                    error_id=error_context.error_id,
                    handler=handler.action_id
                )
                
                return {'success': True, 'result': result, 'handler': handler.action_id}
                
            except Exception as recovery_error:
                error_context.recovery_attempts += 1
                self._update_recovery_stats(handler.action_id, False)
                
                logger.warning(
                    f"Recovery handler failed",
                    error_id=error_context.error_id,
                    handler=handler.action_id,
                    recovery_error=str(recovery_error)
                )
                continue
        
        return {'success': False, 'reason': 'All handlers failed'}
    
    def _find_applicable_handlers(self, error_context: ErrorContext) -> List[RecoveryAction]:
        """Find recovery handlers applicable to the error."""
        handlers = []
        
        # Exact error type match
        if error_context.error_type in self.error_handlers:
            handlers.extend(self.error_handlers[error_context.error_type])
        
        # Component-specific handlers
        component_error_type = f"{error_context.component}_error"
        if component_error_type in self.error_handlers:
            handlers.extend(self.error_handlers[component_error_type])
        
        # Generic handlers based on error class
        error_class = error_context.error_type.lower()
        for handler_type in self.error_handlers:
            if handler_type in error_class or error_class in handler_type:
                handlers.extend(self.error_handlers[handler_type])
        
        # Remove duplicates and sort by priority
        unique_handlers = list({h.action_id: h for h in handlers}.values())
        unique_handlers.sort(key=lambda x: x.priority, reverse=True)
        
        return unique_handlers
    
    def _should_circuit_break(self, component: str, operation: str) -> bool:
        """Check if circuit breaker should activate."""
        key = f"{component}_{operation}"
        
        if key not in self.circuit_breakers:
            self.circuit_breakers[key] = {
                'failure_count': 0,
                'last_failure': 0,
                'state': 'closed'  # closed, open, half-open
            }
        
        breaker = self.circuit_breakers[key]
        current_time = time.time()
        
        # Reset if timeout has passed
        if (breaker['state'] == 'open' and 
            current_time - breaker['last_failure'] > self.config['circuit_breaker_timeout']):
            breaker['state'] = 'half-open'
            breaker['failure_count'] = 0
        
        # Increment failure count
        breaker['failure_count'] += 1
        breaker['last_failure'] = current_time
        
        # Check if threshold exceeded
        if breaker['failure_count'] >= self.config['circuit_breaker_threshold']:
            breaker['state'] = 'open'
            return True
        
        return False
    
    def _update_recovery_stats(self, handler_id: str, success: bool):
        """Update recovery statistics."""
        if handler_id not in self.recovery_stats:
            self.recovery_stats[handler_id] = {
                'attempts': 0,
                'successes': 0,
                'failures': 0,
                'success_rate': 0.0
            }
        
        stats = self.recovery_stats[handler_id]
        stats['attempts'] += 1
        
        if success:
            stats['successes'] += 1
        else:
            stats['failures'] += 1
        
        stats['success_rate'] = stats['successes'] / stats['attempts']
    
    def _cleanup_error_history(self):
        """Clean up old error history entries."""
        if len(self.error_history) > self.config['max_error_history']:
            self.error_history = self.error_history[-self.config['max_error_history']:]
    
    # Default recovery handlers
    async def _switch_ai_provider(self, error_context: ErrorContext) -> Any:
        """Switch to backup AI provider."""
        # This would be implemented to switch to a backup provider
        # For now, return a placeholder
        return {
            'recovery_action': 'switched_provider',
            'new_provider': 'backup_provider',
            'message': 'Switched to backup AI provider due to error'
        }
    
    async def _retry_with_backoff(self, error_context: ErrorContext) -> Any:
        """Retry operation with exponential backoff."""
        attempt = error_context.recovery_attempts
        delay = min(2 ** attempt, 30)  # Cap at 30 seconds
        
        logger.info(f"Retrying with backoff", delay=delay, attempt=attempt)
        await asyncio.sleep(delay)
        
        # The actual retry would happen in the calling code
        # This just provides the delay mechanism
        return {
            'recovery_action': 'retry_scheduled',
            'delay': delay,
            'attempt': attempt
        }
    
    async def _fallback_parsing(self, error_context: ErrorContext) -> Any:
        """Use fallback parsing method."""
        return {
            'recovery_action': 'fallback_parsing',
            'content': 'Raw content due to parsing error',
            'error': error_context.error_message
        }
    
    async def _graceful_rendering_fallback(self, error_context: ErrorContext) -> Any:
        """Provide graceful rendering fallback."""
        return {
            'recovery_action': 'graceful_fallback',
            'render_mode': 'simple',
            'content': 'Simplified rendering due to error',
            'error': error_context.error_message
        }
    
    async def _try_alternative_tool(self, error_context: ErrorContext) -> Any:
        """Try alternative tool or method."""
        return {
            'recovery_action': 'alternative_tool',
            'tool': 'fallback_tool',
            'message': 'Using alternative tool due to error'
        }
    
    # Monitoring and reporting
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors."""
        recent_errors = [e for e in self.error_history if time.time() - e.timestamp < 3600]  # Last hour
        
        error_counts = {}
        component_errors = {}
        
        for error in recent_errors:
            error_counts[error.error_type] = error_counts.get(error.error_type, 0) + 1
            component_errors[error.component] = component_errors.get(error.component, 0) + 1
        
        return {
            'total_errors': len(self.error_history),
            'recent_errors': len(recent_errors),
            'error_types': error_counts,
            'component_errors': component_errors,
            'recovery_stats': self.recovery_stats,
            'circuit_breakers': {k: v for k, v in self.circuit_breakers.items() if v['state'] != 'closed'}
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status."""
        recent_errors = [e for e in self.error_history if time.time() - e.timestamp < 3600]
        critical_errors = [e for e in recent_errors if e.severity == ErrorSeverity.CRITICAL]
        
        # Calculate health score (0-100)
        health_score = 100
        if recent_errors:
            health_score -= min(len(recent_errors) * 2, 30)  # -2 per error, max -30
        if critical_errors:
            health_score -= len(critical_errors) * 20  # -20 per critical error
        
        health_score = max(0, health_score)
        
        status = 'healthy'
        if health_score < 50:
            status = 'degraded'
        if health_score < 20:
            status = 'critical'
        if critical_errors:
            status = 'critical'
        
        return {
            'status': status,
            'health_score': health_score,
            'recent_errors': len(recent_errors),
            'critical_errors': len(critical_errors),
            'active_circuit_breakers': len([b for b in self.circuit_breakers.values() if b['state'] == 'open']),
            'recovery_success_rate': self._calculate_overall_recovery_rate()
        }
    
    def _calculate_overall_recovery_rate(self) -> float:
        """Calculate overall recovery success rate."""
        if not self.recovery_stats:
            return 0.0
        
        total_attempts = sum(stats['attempts'] for stats in self.recovery_stats.values())
        total_successes = sum(stats['successes'] for stats in self.recovery_stats.values())
        
        return total_successes / total_attempts if total_attempts > 0 else 0.0
    
    def reset_circuit_breaker(self, component: str, operation: str):
        """Manually reset a circuit breaker."""
        key = f"{component}_{operation}"
        if key in self.circuit_breakers:
            self.circuit_breakers[key] = {
                'failure_count': 0,
                'last_failure': 0,
                'state': 'closed'
            }
            logger.info(f"Circuit breaker reset", component=component, operation=operation)
    
    def clear_error_history(self):
        """Clear error history."""
        self.error_history.clear()
        logger.info("Error history cleared")
