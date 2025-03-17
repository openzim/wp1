import attr
import json
import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Union

from wp1.constants import MAX_ARTICLES_BEFORE_COMMIT


class CombinatorOperationType(Enum):
    """Operations that can be performed between selections."""
    UNION = auto()
    INTERSECTION = auto()
    DIFFERENCE = auto()


@attr.s(slots=True)
class CombinatorComponent:
    """A component in a combinator selection, referencing another selection with an operation."""
    # The ID of the referenced selection
    selection_id = attr.ib(type=int)
    
    # The operation to apply with this component
    operation = attr.ib(type=CombinatorOperationType)
    
    # Optional group ID for nested operations (like parentheses in expressions)
    group_id = attr.ib(type=Optional[int], default=None)
    
    # Execution order within the same group
    order = attr.ib(type=int, default=0)
    
    # Type of the referenced selection (for optimization and display)
    selection_type = attr.ib(type=str, default=None)
    
    # Estimated size of the selection (for optimization)
    estimated_size = attr.ib(type=Optional[int], default=None)
    
    # Status of this component's execution
    execution_status = attr.ib(type=str, default="pending")


@attr.s(slots=True)
class CombinatorExecution:
    """Metadata about a combinator execution."""
    # Timestamp when execution started
    started_at = attr.ib(type=datetime.datetime)
    
    # Timestamp when execution completed (if done)
    completed_at = attr.ib(type=Optional[datetime.datetime], default=None)
    
    # Status of the overall execution
    status = attr.ib(type=str, default="pending")
    
    # Job IDs for each component
    component_jobs = attr.ib(type=Dict[int, str], factory=dict)
    
    # Errors encountered during execution
    errors = attr.ib(type=List[str], factory=list)
    
    # Result size after execution
    result_size = attr.ib(type=Optional[int], default=None)
    
    # Cache key for the result
    result_cache_key = attr.ib(type=Optional[str], default=None)


@attr.s(slots=True)
class CombinatorSelection:
    """Model for storing combinator selections."""
    # Database fields
    id = attr.ib(type=int, default=None)
    c_name = attr.ib(type=str)
    c_user_id = attr.ib(type=str)
    c_project = attr.ib(type=str, default=None)
    c_created_at = attr.ib(type=datetime.datetime, factory=datetime.datetime.now)
    c_updated_at = attr.ib(type=datetime.datetime, factory=datetime.datetime.now)
    
    # Components as JSON string in DB, parsed to list of CombinatorComponent
    c_components_json = attr.ib(type=str, default="{}")
    
    # Last execution metadata as JSON string in DB
    c_execution_json = attr.ib(type=str, default="{}")
    
    # Description provided by user
    c_description = attr.ib(type=str, default="")
    
    # Final selection ID (if materialized)
    c_selection_id = attr.ib(type=Optional[int], default=None)
    
    # Size limit for the final selection
    c_max_size = attr.ib(type=int, default=MAX_ARTICLES_BEFORE_COMMIT)
    
    # Whether to automatically update when component selections change
    c_auto_update = attr.ib(type=bool, default=False)
    
    @property
    def components(self) -> List[CombinatorComponent]:
        """Get the list of components from the JSON string."""
        components_data = json.loads(self.c_components_json)
        result = []
        for comp_data in components_data:
            component = CombinatorComponent(
                selection_id=comp_data['selection_id'],
                operation=CombinatorOperationType[comp_data['operation']],
                group_id=comp_data.get('group_id'),
                order=comp_data.get('order', 0),
                selection_type=comp_data.get('selection_type'),
                estimated_size=comp_data.get('estimated_size'),
                execution_status=comp_data.get('execution_status', 'pending')
            )
            result.append(component)
        return result
    
    @components.setter
    def components(self, components: List[CombinatorComponent]) -> None:
        """Set the components and update the JSON string."""
        components_data = []
        for component in components:
            comp_data = {
                'selection_id': component.selection_id,
                'operation': component.operation.name,
                'group_id': component.group_id,
                'order': component.order,
                'selection_type': component.selection_type,
                'estimated_size': component.estimated_size,
                'execution_status': component.execution_status
            }
            components_data.append(comp_data)
        self.c_components_json = json.dumps(components_data)
    
    @property
    def execution(self) -> Optional[CombinatorExecution]:
        """Get the execution metadata from the JSON string."""
        if not self.c_execution_json or self.c_execution_json == "{}":
            return None
        
        execution_data = json.loads(self.c_execution_json)
        return CombinatorExecution(
            started_at=datetime.datetime.fromisoformat(execution_data['started_at']),
            completed_at=datetime.datetime.fromisoformat(execution_data['completed_at']) 
                if 'completed_at' in execution_data and execution_data['completed_at'] 
                else None,
            status=execution_data.get('status', 'pending'),
            component_jobs=execution_data.get('component_jobs', {}),
            errors=execution_data.get('errors', []),
            result_size=execution_data.get('result_size'),
            result_cache_key=execution_data.get('result_cache_key')
        )
    
    @execution.setter
    def execution(self, execution: CombinatorExecution) -> None:
        """Set the execution metadata and update the JSON string."""
        if execution is None:
            self.c_execution_json = "{}"
            return
        
        execution_data = {
            'started_at': execution.started_at.isoformat(),
            'status': execution.status,
            'component_jobs': execution.component_jobs,
            'errors': execution.errors,
        }
        
        if execution.completed_at:
            execution_data['completed_at'] = execution.completed_at.isoformat()
        
        if execution.result_size is not None:
            execution_data['result_size'] = execution.result_size
            
        if execution.result_cache_key:
            execution_data['result_cache_key'] = execution.result_cache_key
            
        self.c_execution_json = json.dumps(execution_data)
    
    def to_web_dict(self) -> Dict[str, any]:
        """Convert the model to a dictionary for web API responses."""
        result = {
            'id': self.id,
            'name': self.c_name,
            'user_id': self.c_user_id,
            'created_at': self.c_created_at.isoformat(),
            'updated_at': self.c_updated_at.isoformat(),
            'description': self.c_description,
            'project': self.c_project,
            'selection_id': self.c_selection_id,
            'max_size': self.c_max_size,
            'auto_update': self.c_auto_update,
            'components': []
        }
        
        # Add components in a web-friendly format
        for component in self.components:
            result['components'].append({
                'selection_id': component.selection_id,
                'operation': component.operation.name,
                'group_id': component.group_id,
                'order': component.order,
                'selection_type': component.selection_type,
                'estimated_size': component.estimated_size,
                'execution_status': component.execution_status
            })
        
        # Add execution data if available
        if self.execution:
            execution = {
                'started_at': self.execution.started_at.isoformat(),
                'status': self.execution.status,
                'errors': self.execution.errors,
                'result_size': self.execution.result_size
            }
            
            if self.execution.completed_at:
                execution['completed_at'] = self.execution.completed_at.isoformat()
                
            result['execution'] = execution
        
        return result

    def estimate_result_size(self, selection_sizes: Dict[int, int]) -> Optional[int]:
        """
        Estimate the size of the result based on the operation types and input sizes.
        
        Args:
            selection_sizes: Dictionary mapping selection IDs to their sizes
            
        Returns:
            Estimated size of the result, or None if cannot be estimated
        """
        # Group components by group_id
        groups = {}
        for component in sorted(self.components, key=lambda c: c.order):
            group_id = component.group_id or 0  # Use 0 as default group
            if group_id not in groups:
                groups[group_id] = []
            groups[group_id].append(component)
        
        # Process each group
        group_results = {}
        for group_id, components in groups.items():
            if not components:
                continue
                
            # Start with the first component's selection size
            first = components[0]
            if first.selection_id not in selection_sizes:
                return None  # Cannot estimate if size unknown
                
            estimated = selection_sizes[first.selection_id]
            
            # Apply operations in order
            for component in components[1:]:
                if component.selection_id not in selection_sizes:
                    return None  # Cannot estimate if size unknown
                    
                comp_size = selection_sizes[component.selection_id]
                
                if component.operation == CombinatorOperationType.UNION:
                    # Union: We take a conservative approach and assume some overlap
                    # Estimate as sum minus 20% overlap
                    estimated = int(estimated + comp_size - (min(estimated, comp_size) * 0.2))
                
                elif component.operation == CombinatorOperationType.INTERSECTION:
                    # Intersection: We estimate as 50% of the smaller set (conservative)
                    estimated = int(min(estimated, comp_size) * 0.5)
                
                elif component.operation == CombinatorOperationType.DIFFERENCE:
                    # Difference: We estimate as current minus 80% of overlap with second
                    # This is conservative for large second sets
                    estimated = max(0, int(estimated - (min(estimated, comp_size) * 0.8)))
            
            group_results[group_id] = estimated
        
        # Combine group results (assuming implicit union between groups)
        final_estimate = 0
        for size in group_results.values():
            final_estimate += size
        
        return final_estimate