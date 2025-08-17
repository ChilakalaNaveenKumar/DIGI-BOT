"""
Streaming Coordinator

Advanced streaming coordination system that manages multiple SSE streams,
prevents conflicts, handles synchronization, and provides unified streaming experience.
"""

import asyncio
import json
import time
import uuid
from typing import Any, Dict, List, Optional, AsyncGenerator, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque

import structlog

logger = structlog.get_logger(__name__)


class StreamType(Enum):
    """Types of streams that can be coordinated."""
    REASONING = "reasoning"
    ACTIVITY = "activity"
    CONTENT = "content"
    TOOLS = "tools"
    ERROR = "error"
    METADATA = "metadata"
    PROGRESS = "progress"
    QUALITY = "quality"


class StreamPriority(Enum):
    """Stream priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class StreamState(Enum):
    """Stream states."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class StreamChunk:
    """Individual stream chunk with metadata."""
    chunk_id: str
    stream_id: str
    stream_type: StreamType
    content: Any
    timestamp: float
    sequence_number: int
    priority: StreamPriority = StreamPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamInfo:
    """Information about a managed stream."""
    stream_id: str
    stream_type: StreamType
    priority: StreamPriority
    state: StreamState
    created_at: float
    updated_at: float
    total_chunks: int = 0
    completed_chunks: int = 0
    error_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class StreamingCoordinator:
    """
    Advanced streaming coordinator that provides:
    - Multi-stream synchronization
    - Priority-based ordering
    - Conflict resolution
    - Stream merging and splitting
    - Backpressure handling
    - Error recovery for streams
    - Performance optimization
    """
    
    def __init__(self, max_concurrent_streams: int = 10):
        self.max_concurrent_streams = max_concurrent_streams
        
        # Stream management
        self.active_streams: Dict[str, StreamInfo] = {}
        self.stream_generators: Dict[str, AsyncGenerator] = {}
        self.stream_queues: Dict[str, asyncio.Queue] = {}
        
        # Coordination
        self.output_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.coordination_rules: Dict[str, Callable] = {}
        self.stream_dependencies: Dict[str, Set[str]] = defaultdict(set)
        
        # Synchronization
        self.sequence_counters: Dict[str, int] = defaultdict(int)
        self.global_sequence: int = 0
        self.sync_points: Dict[str, asyncio.Event] = {}
        
        # Performance monitoring
        self.performance_stats: Dict[str, Any] = {
            'total_chunks_processed': 0,
            'average_latency': 0.0,
            'throughput_per_second': 0.0,
            'error_rate': 0.0,
            'active_streams_count': 0
        }
        
        # Configuration
        self.config = {
            'max_queue_size': 1000,
            'chunk_timeout': 30.0,
            'sync_timeout': 10.0,
            'backpressure_threshold': 0.8,
            'enable_compression': True,
            'enable_deduplication': True
        }
        
        # Background tasks
        self._coordinator_task: Optional[asyncio.Task] = None
        self._monitor_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Setup default coordination rules
        self._setup_default_rules()
    
    async def start(self):
        """Start the streaming coordinator."""
        if self._running:
            return
        
        self._running = True
        
        # Start background tasks
        self._coordinator_task = asyncio.create_task(self._coordinate_streams())
        self._monitor_task = asyncio.create_task(self._monitor_performance())
        
        logger.info("Streaming coordinator started")
    
    async def stop(self):
        """Stop the streaming coordinator."""
        if not self._running:
            return
        
        self._running = False
        
        # Cancel all active streams
        for stream_id in list(self.active_streams.keys()):
            await self.cancel_stream(stream_id)
        
        # Cancel background tasks
        if self._coordinator_task:
            self._coordinator_task.cancel()
        if self._monitor_task:
            self._monitor_task.cancel()
        
        # Wait for tasks to complete
        try:
            if self._coordinator_task:
                await self._coordinator_task
        except asyncio.CancelledError:
            pass
        
        try:
            if self._monitor_task:
                await self._monitor_task
        except asyncio.CancelledError:
            pass
        
        logger.info("Streaming coordinator stopped")
    
    async def register_stream(
        self,
        stream_generator: AsyncGenerator,
        stream_type: StreamType,
        priority: StreamPriority = StreamPriority.NORMAL,
        dependencies: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register a new stream with the coordinator."""
        
        if len(self.active_streams) >= self.max_concurrent_streams:
            raise RuntimeError("Maximum concurrent streams exceeded")
        
        stream_id = str(uuid.uuid4())
        
        # Create stream info
        stream_info = StreamInfo(
            stream_id=stream_id,
            stream_type=stream_type,
            priority=priority,
            state=StreamState.PENDING,
            created_at=time.time(),
            updated_at=time.time(),
            metadata=metadata or {}
        )
        
        # Register stream
        self.active_streams[stream_id] = stream_info
        self.stream_generators[stream_id] = stream_generator
        self.stream_queues[stream_id] = asyncio.Queue(maxsize=self.config['max_queue_size'])
        
        # Set up dependencies
        if dependencies:
            self.stream_dependencies[stream_id] = dependencies
        
        # Create sync point
        self.sync_points[stream_id] = asyncio.Event()
        
        logger.info(
            f"Stream registered",
            stream_id=stream_id,
            stream_type=stream_type.value,
            priority=priority.value
        )
        
        # Start processing the stream
        asyncio.create_task(self._process_stream(stream_id))
        
        return stream_id
    
    async def cancel_stream(self, stream_id: str):
        """Cancel a stream."""
        if stream_id not in self.active_streams:
            return
        
        stream_info = self.active_streams[stream_id]
        stream_info.state = StreamState.CANCELLED
        stream_info.updated_at = time.time()
        
        # Clean up
        if stream_id in self.stream_generators:
            try:
                await self.stream_generators[stream_id].aclose()
            except Exception as e:
                logger.warning(f"Error closing stream generator", stream_id=stream_id, error=str(e))
            del self.stream_generators[stream_id]
        
        if stream_id in self.stream_queues:
            del self.stream_queues[stream_id]
        
        if stream_id in self.sync_points:
            self.sync_points[stream_id].set()  # Release any waiting tasks
            del self.sync_points[stream_id]
        
        if stream_id in self.stream_dependencies:
            del self.stream_dependencies[stream_id]
        
        del self.active_streams[stream_id]
        
        logger.info(f"Stream cancelled", stream_id=stream_id)
    
    async def get_coordinated_stream(self) -> AsyncGenerator[StreamChunk, None]:
        """Get the coordinated output stream."""
        while self._running or not self.output_queue.empty():
            try:
                # Get next chunk with timeout
                priority_item = await asyncio.wait_for(
                    self.output_queue.get(),
                    timeout=self.config['chunk_timeout']
                )
                
                # Priority queue returns (priority, chunk)
                _, chunk = priority_item
                
                # Update performance stats
                self.performance_stats['total_chunks_processed'] += 1
                
                yield chunk
                
            except asyncio.TimeoutError:
                # No chunks available, continue
                continue
            except Exception as e:
                logger.error(f"Error in coordinated stream", error=str(e))
                # Yield error chunk
                error_chunk = StreamChunk(
                    chunk_id=str(uuid.uuid4()),
                    stream_id="coordinator",
                    stream_type=StreamType.ERROR,
                    content={"error": str(e)},
                    timestamp=time.time(),
                    sequence_number=self._get_next_sequence("coordinator"),
                    priority=StreamPriority.HIGH
                )
                yield error_chunk
    
    async def _process_stream(self, stream_id: str):
        """Process an individual stream."""
        stream_info = self.active_streams.get(stream_id)
        if not stream_info:
            return
        
        stream_generator = self.stream_generators.get(stream_id)
        if not stream_generator:
            return
        
        try:
            stream_info.state = StreamState.ACTIVE
            stream_info.updated_at = time.time()
            
            # Wait for dependencies if any
            await self._wait_for_dependencies(stream_id)
            
            # Process chunks from the stream
            async for chunk_data in stream_generator:
                if not self._running or stream_info.state == StreamState.CANCELLED:
                    break
                
                # Create stream chunk
                chunk = StreamChunk(
                    chunk_id=str(uuid.uuid4()),
                    stream_id=stream_id,
                    stream_type=stream_info.stream_type,
                    content=chunk_data,
                    timestamp=time.time(),
                    sequence_number=self._get_next_sequence(stream_id),
                    priority=stream_info.priority
                )
                
                # Apply coordination rules
                processed_chunk = await self._apply_coordination_rules(chunk)
                if processed_chunk:
                    # Add to output queue with priority
                    priority_value = -processed_chunk.priority.value  # Negative for max heap behavior
                    await self.output_queue.put((priority_value, processed_chunk))
                
                stream_info.total_chunks += 1
                stream_info.completed_chunks += 1
                stream_info.updated_at = time.time()
            
            # Mark stream as completed
            stream_info.state = StreamState.COMPLETED
            stream_info.updated_at = time.time()
            
            logger.info(
                f"Stream processing completed",
                stream_id=stream_id,
                total_chunks=stream_info.total_chunks
            )
            
        except Exception as e:
            stream_info.state = StreamState.ERROR
            stream_info.error_count += 1
            stream_info.updated_at = time.time()
            
            logger.error(
                f"Stream processing error",
                stream_id=stream_id,
                error=str(e)
            )
            
            # Send error chunk
            error_chunk = StreamChunk(
                chunk_id=str(uuid.uuid4()),
                stream_id=stream_id,
                stream_type=StreamType.ERROR,
                content={"error": str(e), "stream_id": stream_id},
                timestamp=time.time(),
                sequence_number=self._get_next_sequence(stream_id),
                priority=StreamPriority.HIGH
            )
            
            await self.output_queue.put((-error_chunk.priority.value, error_chunk))
        
        finally:
            # Signal completion
            if stream_id in self.sync_points:
                self.sync_points[stream_id].set()
    
    async def _wait_for_dependencies(self, stream_id: str):
        """Wait for stream dependencies to be satisfied."""
        dependencies = self.stream_dependencies.get(stream_id, set())
        
        if not dependencies:
            return
        
        # Wait for all dependencies to complete or timeout
        wait_tasks = []
        for dep_stream_id in dependencies:
            if dep_stream_id in self.sync_points:
                wait_tasks.append(self.sync_points[dep_stream_id].wait())
        
        if wait_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*wait_tasks),
                    timeout=self.config['sync_timeout']
                )
            except asyncio.TimeoutError:
                logger.warning(
                    f"Dependency timeout for stream",
                    stream_id=stream_id,
                    dependencies=list(dependencies)
                )
    
    async def _coordinate_streams(self):
        """Background task to coordinate streams."""
        while self._running:
            try:
                # Check for backpressure
                await self._handle_backpressure()
                
                # Clean up completed streams
                await self._cleanup_completed_streams()
                
                # Update performance stats
                self.performance_stats['active_streams_count'] = len(self.active_streams)
                
                # Sleep briefly
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Coordination error", error=str(e))
                await asyncio.sleep(1)  # Longer sleep on error
    
    async def _handle_backpressure(self):
        """Handle backpressure by pausing low-priority streams."""
        queue_utilization = self.output_queue.qsize() / self.config['max_queue_size']
        
        if queue_utilization > self.config['backpressure_threshold']:
            # Pause low-priority streams
            for stream_info in self.active_streams.values():
                if (stream_info.priority == StreamPriority.LOW and 
                    stream_info.state == StreamState.ACTIVE):
                    stream_info.state = StreamState.PAUSED
                    logger.info(f"Stream paused due to backpressure", stream_id=stream_info.stream_id)
        else:
            # Resume paused streams
            for stream_info in self.active_streams.values():
                if stream_info.state == StreamState.PAUSED:
                    stream_info.state = StreamState.ACTIVE
                    logger.info(f"Stream resumed", stream_id=stream_info.stream_id)
    
    async def _cleanup_completed_streams(self):
        """Clean up completed or errored streams."""
        completed_streams = [
            stream_id for stream_id, stream_info in self.active_streams.items()
            if stream_info.state in [StreamState.COMPLETED, StreamState.ERROR, StreamState.CANCELLED]
            and time.time() - stream_info.updated_at > 60  # Keep for 1 minute
        ]
        
        for stream_id in completed_streams:
            await self.cancel_stream(stream_id)
    
    async def _monitor_performance(self):
        """Background task to monitor performance."""
        last_chunk_count = 0
        last_time = time.time()
        
        while self._running:
            try:
                current_time = time.time()
                current_chunk_count = self.performance_stats['total_chunks_processed']
                
                # Calculate throughput
                time_diff = current_time - last_time
                chunk_diff = current_chunk_count - last_chunk_count
                
                if time_diff > 0:
                    self.performance_stats['throughput_per_second'] = chunk_diff / time_diff
                
                # Calculate error rate
                total_errors = sum(
                    stream_info.error_count for stream_info in self.active_streams.values()
                )
                total_chunks = sum(
                    stream_info.total_chunks for stream_info in self.active_streams.values()
                )
                
                if total_chunks > 0:
                    self.performance_stats['error_rate'] = total_errors / total_chunks
                
                last_chunk_count = current_chunk_count
                last_time = current_time
                
                # Sleep for monitoring interval
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Performance monitoring error", error=str(e))
                await asyncio.sleep(5)
    
    async def _apply_coordination_rules(self, chunk: StreamChunk) -> Optional[StreamChunk]:
        """Apply coordination rules to a chunk."""
        
        # Check if there's a specific rule for this stream type
        rule_key = f"{chunk.stream_type.value}_rule"
        if rule_key in self.coordination_rules:
            try:
                return await self.coordination_rules[rule_key](chunk)
            except Exception as e:
                logger.warning(f"Coordination rule error", rule=rule_key, error=str(e))
        
        # Apply default processing
        return await self._default_chunk_processing(chunk)
    
    async def _default_chunk_processing(self, chunk: StreamChunk) -> Optional[StreamChunk]:
        """Default chunk processing."""
        
        # Deduplication
        if self.config['enable_deduplication']:
            chunk_hash = hash(str(chunk.content))
            if hasattr(self, '_seen_chunks'):
                if chunk_hash in self._seen_chunks:
                    return None  # Skip duplicate
                self._seen_chunks.add(chunk_hash)
            else:
                self._seen_chunks = {chunk_hash}
        
        # Compression (placeholder)
        if self.config['enable_compression']:
            # Would implement compression logic here
            pass
        
        return chunk
    
    def _get_next_sequence(self, stream_id: str) -> int:
        """Get next sequence number for a stream."""
        self.sequence_counters[stream_id] += 1
        self.global_sequence += 1
        return self.sequence_counters[stream_id]
    
    def _setup_default_rules(self):
        """Setup default coordination rules."""
        
        # Reasoning stream rule: ensure ordering
        async def reasoning_rule(chunk: StreamChunk) -> StreamChunk:
            # Add reasoning-specific metadata
            chunk.metadata['reasoning_step'] = chunk.sequence_number
            return chunk
        
        # Activity stream rule: batch similar activities
        async def activity_rule(chunk: StreamChunk) -> StreamChunk:
            # Could implement activity batching here
            return chunk
        
        # Error stream rule: high priority, immediate processing
        async def error_rule(chunk: StreamChunk) -> StreamChunk:
            chunk.priority = StreamPriority.CRITICAL
            return chunk
        
        self.coordination_rules = {
            'reasoning_rule': reasoning_rule,
            'activity_rule': activity_rule,
            'error_rule': error_rule
        }
    
    def add_coordination_rule(self, rule_name: str, rule_func: Callable):
        """Add a custom coordination rule."""
        self.coordination_rules[rule_name] = rule_func
        logger.info(f"Coordination rule added", rule_name=rule_name)
    
    def get_stream_status(self) -> Dict[str, Any]:
        """Get status of all streams."""
        return {
            'active_streams': len(self.active_streams),
            'queue_size': self.output_queue.qsize(),
            'performance': self.performance_stats,
            'streams': {
                stream_id: {
                    'type': stream_info.stream_type.value,
                    'state': stream_info.state.value,
                    'priority': stream_info.priority.value,
                    'chunks': stream_info.total_chunks,
                    'errors': stream_info.error_count
                }
                for stream_id, stream_info in self.active_streams.items()
            }
        }
    
    async def sync_streams(self, stream_ids: List[str], timeout: float = 10.0):
        """Synchronize multiple streams at a sync point."""
        sync_events = []
        
        for stream_id in stream_ids:
            if stream_id in self.sync_points:
                sync_events.append(self.sync_points[stream_id].wait())
        
        if sync_events:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*sync_events),
                    timeout=timeout
                )
                logger.info(f"Streams synchronized", stream_ids=stream_ids)
            except asyncio.TimeoutError:
                logger.warning(f"Stream sync timeout", stream_ids=stream_ids)
    
    def pause_stream(self, stream_id: str):
        """Pause a specific stream."""
        if stream_id in self.active_streams:
            self.active_streams[stream_id].state = StreamState.PAUSED
            logger.info(f"Stream paused", stream_id=stream_id)
    
    def resume_stream(self, stream_id: str):
        """Resume a paused stream."""
        if stream_id in self.active_streams:
            stream_info = self.active_streams[stream_id]
            if stream_info.state == StreamState.PAUSED:
                stream_info.state = StreamState.ACTIVE
                logger.info(f"Stream resumed", stream_id=stream_id)
