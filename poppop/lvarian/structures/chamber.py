"""
L'Varian τ-ary Panto-Topological Structures
Implements τ-ary trees, coherence rays, and panto-topological manifolds
for storing and retrieving post-ictal work context.
"""

import time
import hashlib
import json
from collections import deque

# Import from parent package
from .. import TAU, TAU_ARY_BASE, TAU_ARY_DEPTH, COHERENCE_RAY_LENGTH, COHERENCE_MIN


class TauAryNode:
    """
    L'Varian τ-ary Tree Node
    Each node can have up to TAU_ARY_BASE (13) children.
    Stores work context data with κ-strain metadata.
    """
    
    def __init__(self, node_id, data=None):
        """
        Initialize a τ-ary node.
        
        Args:
            node_id: Unique identifier
            data: Work context data (dict)
        """
        self.node_id = node_id
        self.data = data if data else {}
        self.children = {}  # key: child_id, value: TauAryNode
        self.parent = None
        self.kappa_value = 0.0  # κ-strain at this node
        self.coherence = 0.0   # Coherence score
        self.depth = 0          # Depth in the tree
    
    def add_child(self, child_id, data=None):
        """
        Add a child node.
        Enforces τ-ary limit (max TAU_ARY_BASE children).
        """
        if len(self.children) >= TAU_ARY_BASE:
            # Cannot add more children (τ-ary limit)
            return None
        
        child = TauAryNode(child_id, data)
        child.parent = self
        child.depth = self.depth + 1
        self.children[child_id] = child
        return child
    
    def get_child(self, child_id):
        """Get a child by ID."""
        return self.children.get(child_id)
    
    def remove_child(self, child_id):
        """Remove a child by ID."""
        if child_id in self.children:
            del self.children[child_id]
    
    def update_data(self, data):
        """Update node data."""
        self.data.update(data)
    
    def set_kappa(self, kappa):
        """Set κ-strain value."""
        self.kappa_value = kappa
    
    def set_coherence(self, coherence):
        """Set coherence score."""
        self.coherence = coherence
    
    def get_status(self):
        """Get node status."""
        return {
            'node_id': self.node_id,
            'depth': self.depth,
            'kappa': self.kappa_value,
            'coherence': self.coherence,
            'child_count': len(self.children),
            'data_keys': list(self.data.keys())
        }


class TauAryTree:
    """
    L'Varian τ-ary Tree
    A tree where each node has at most TAU_ARY_BASE children.
    Used for hierarchical storage of work context.
    """
    
    def __init__(self, root_id='root'):
        """Initialize with root node."""
        self.root = TauAryNode(root_id)
        self._node_map = {root_id: self.root}
        self._depth = 0
    
    def add_node(self, parent_id, node_id, data=None):
        """
        Add a node to the tree.
        
        Args:
            parent_id: ID of parent node
            node_id: ID of new node
            data: Data for new node
        
        Returns:
            New node or None if failed
        """
        parent = self._node_map.get(parent_id)
        if not parent:
            return None
        
        node = parent.add_child(node_id, data)
        if node:
            self._node_map[node_id] = node
            if node.depth > self._depth:
                self._depth = node.depth
        return node
    
    def get_node(self, node_id):
        """Get node by ID."""
        return self._node_map.get(node_id)
    
    def find_nodes_by_kappa(self, min_kappa, max_kappa=None):
        """Find nodes with κ in range."""
        results = []
        for node in self._node_map.values():
            if node.kappa_value >= min_kappa:
                if max_kappa is None or node.kappa_value <= max_kappa:
                    results.append(node)
        return results
    
    def get_path(self, node_id):
        """Get path from root to node."""
        path = []
        node = self._node_map.get(node_id)
        while node:
            path.insert(0, node)
            node = node.parent
        return path
    
    def get_depth(self):
        """Get maximum depth of tree."""
        return self._depth
    
    def get_size(self):
        """Get total number of nodes."""
        return len(self._node_map)
    
    def traverse_breadth_first(self):
        """Breadth-first traversal."""
        nodes = []
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            nodes.append(node)
            for child in node.children.values():
                queue.append(child)
        return nodes
    
    def traverse_depth_first(self):
        """Depth-first traversal."""
        nodes = []
        stack = [self.root]
        while stack:
            node = stack.pop()
            nodes.append(node)
            # Push children in reverse order for correct traversal
            for child in reversed(list(node.children.values())):
                stack.append(child)
        return nodes


class CoherenceRay:
    """
    L'Varian Coherence Ray
    A linear sequence of nodes representing a coherent work thread.
    Used to track focused work sessions through the manifold.
    """
    
    def __init__(self, ray_id, max_length=COHERENCE_RAY_LENGTH):
        """
        Initialize a coherence ray.
        
        Args:
            ray_id: Unique ray identifier
            max_length: Maximum length of ray
        """
        self.ray_id = ray_id
        self.max_length = max_length
        self.nodes = []  # Ordered list of node references
        self.kappa_sum = 0.0
        self.coherence_score = 0.0
    
    def add_node(self, node):
        """
        Add a node to the ray.
        
        Returns:
            True if added, False if ray is full
        """
        if len(self.nodes) >= self.max_length:
            return False
        
        self.nodes.append(node)
        self.kappa_sum += node.kappa_value
        self._update_coherence()
        return True
    
    def _update_coherence(self):
        """Update coherence score based on nodes."""
        if not self.nodes:
            self.coherence_score = 0.0
            return
        
        # L'Varian coherence: harmonic mean of node coherences weighted by κ
        total_weight = 0.0
        weighted_sum = 0.0
        
        for node in self.nodes:
            weight = node.kappa_value + 0.1  # Avoid zero division
            weighted_sum += node.coherence * weight
            total_weight += weight
        
        if total_weight > 0:
            self.coherence_score = weighted_sum / total_weight
        else:
            self.coherence_score = 0.0
    
    def get_coherence(self):
        """Get coherence score."""
        return self.coherence_score
    
    def is_coherent(self):
        """Check if ray meets minimum coherence threshold."""
        return self.coherence_score >= COHERENCE_MIN
    
    def get_kappa_sum(self):
        """Get sum of κ values in ray."""
        return self.kappa_sum
    
    def get_length(self):
        """Get number of nodes in ray."""
        return len(self.nodes)


class PantoTopologicalManifold:
    """
    L'Varian Panto-Topological Manifold
    A multi-dimensional structure combining τ-ary trees and coherence rays
    for storing and navigating work context.
    """
    
    def __init__(self, manifold_id='main'):
        """Initialize the manifold."""
        self.manifold_id = manifold_id
        self.tree = TauAryTree(f'{manifold_id}_root')
        self.rays = {}  # ray_id -> CoherenceRay
        self._node_to_rays = {}  # node_id -> list of ray_ids
    
    def add_work_context(self, context_id, parent_id=None, data=None, kappa=0.0, coherence=0.0):
        """
        Add a work context to the manifold.
        
        Args:
            context_id: Unique context identifier
            parent_id: Parent context ID (None for root)
            data: Context data
            kappa: κ-strain value
            coherence: Coherence score
        
        Returns:
            Created node
        """
        if parent_id is None:
            parent_id = self.tree.root.node_id
        
        node = self.tree.add_node(parent_id, context_id, data)
        if node:
            node.set_kappa(kappa)
            node.set_coherence(coherence)
            # Auto-create or update rays
            self._update_rays(node)
        return node
    
    def _update_rays(self, node):
        """Update coherence rays with new node."""
        # Find rays that can accommodate this node
        for ray_id, ray in self.rays.items():
            if ray.add_node(node):
                if node.node_id not in self._node_to_rays:
                    self._node_to_rays[node.node_id] = []
                if ray_id not in self._node_to_rays[node.node_id]:
                    self._node_to_rays[node.node_id].append(ray_id)
    
    def create_ray(self, ray_id):
        """Create a new coherence ray."""
        ray = CoherenceRay(ray_id)
        self.rays[ray_id] = ray
        return ray
    
    def get_ray(self, ray_id):
        """Get a ray by ID."""
        return self.rays.get(ray_id)
    
    def get_coherent_rays(self):
        """Get all rays that meet coherence threshold."""
        return [ray for ray in self.rays.values() if ray.is_coherent()]
    
    def find_high_kappa_nodes(self, min_kappa=0.7):
        """Find nodes with κ above threshold."""
        return self.tree.find_nodes_by_kappa(min_kappa)
    
    def get_context_path(self, context_id):
        """Get the path to a context."""
        return self.tree.get_path(context_id)
    
    def get_stats(self):
        """Get manifold statistics."""
        return {
            'node_count': self.tree.get_size(),
            'depth': self.tree.get_depth(),
            'ray_count': len(self.rays),
            'coherent_ray_count': len(self.get_coherent_rays()),
            'high_kappa_nodes': len(self.find_high_kappa_nodes(0.7))
        }


class CoherenceChamber:
    """
    L'Varian Coherence Chamber
    The central structure for PopPop that combines:
    - Panto-topological manifold (work context storage)
    - κ-strain monitoring (gap detection)
    - PCF cycle tracking (work pattern analysis)
    
    This is the main interface for tracking and restoring post-ictal work.
    """
    
    def __init__(self, chamber_id='poppop_main'):
        """Initialize the coherence chamber."""
        self.chamber_id = chamber_id
        self.manifold = PantoTopologicalManifold(f'{chamber_id}_manifold')
        self._work_sessions = []
        self._gap_periods = []
        self._restore_points = []
    
    def record_work(self, session_id, context_data, kappa_monitor, pcf_tracker):
        """
        Record a work session.
        
        Args:
            session_id: Unique session identifier
            context_data: Work context to save
            kappa_monitor: KappaMonitor instance
            pcf_tracker: PFCTracker instance
        """
        # Check for gap (κ collapse)
        if kappa_monitor.has_collapse():
            collapse = kappa_monitor.get_last_collapse()
            self._record_gap(session_id, collapse, pcf_tracker)
        
        # Store work context in manifold
        node = self.manifold.add_work_context(
            context_id=session_id,
            data=context_data,
            kappa=kappa_monitor.get_kappa(),
            coherence=pcf_tracker.get_stats()['average_coherence']
        )
        
        # Save session
        session = {
            'session_id': session_id,
            'timestamp': time.time(),
            'kappa': kappa_monitor.get_kappa(),
            'tau_units': kappa_monitor._tau_timer.get_tau_units(),
            'context_id': session_id,
            'has_gap': kappa_monitor.has_collapse()
        }
        self._work_sessions.append(session)
        
        # If gap detected, create restore point
        if kappa_monitor.has_collapse():
            self._create_restore_point(session_id, kappa_monitor, pcf_tracker)
        
        return node
    
    def _record_gap(self, session_id, collapse_event, pcf_tracker):
        """Record a gap period."""
        gap = {
            'gap_id': f'gap_{session_id}_{int(collapse_event["timestamp"])}',
            'session_id': session_id,
            'collapse_event': collapse_event,
            'timestamp': collapse_event['timestamp'],
            'tau_units': collapse_event['tau_units'],
            'pcf_anomalies': pcf_tracker.get_anomalies()
        }
        self._gap_periods.append(gap)
    
    def _create_restore_point(self, session_id, kappa_monitor, pcf_tracker):
        """Create a restore point for gap recovery."""
        restore_point = {
            'restore_id': f'restore_{session_id}',
            'session_id': session_id,
            'timestamp': time.time(),
            'kappa_snapshot': kappa_monitor.get_status(),
            'pcf_snapshot': pcf_tracker.get_stats(),
            'manifold_snapshot': self.manifold.get_stats()
        }
        self._restore_points.append(restore_point)
    
    def get_gap_periods(self):
        """Get all recorded gap periods."""
        return self._gap_periods
    
    def get_restore_points(self):
        """Get all restore points."""
        return self._restore_points
    
    def get_last_restore_point(self):
        """Get the most recent restore point."""
        if self._restore_points:
            return self._restore_points[-1]
        return None
    
    def restore_context(self, restore_id=None):
        """
        Restore work context from a restore point.
        
        Args:
            restore_id: Specific restore ID (None for latest)
        
        Returns:
            Restored context data
        """
        if restore_id is None:
            restore_point = self.get_last_restore_point()
        else:
            restore_point = next(
                (rp for rp in self._restore_points if rp['restore_id'] == restore_id),
                None
            )
        
        if not restore_point:
            return None
        
        # Find the corresponding work session
        session_id = restore_point['session_id']
        session = next(
            (s for s in self._work_sessions if s['session_id'] == session_id),
            None
        )
        
        if not session:
            return None
        
        # Retrieve context from manifold
        node = self.manifold.get_context_path(session['context_id'])
        
        return {
            'restore_point': restore_point,
            'session': session,
            'context_path': [n.get_status() for n in node] if node else []
        }
    
    def get_stats(self):
        """Get coherence chamber statistics."""
        return {
            'session_count': len(self._work_sessions),
            'gap_count': len(self._gap_periods),
            'restore_point_count': len(self._restore_points),
            'manifold_stats': self.manifold.get_stats()
        }
