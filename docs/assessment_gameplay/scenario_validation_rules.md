# Scenario Validation Rules

## Input Validation
1. **Scenario ID Format**
   - Must match pattern: [A-Z]{2,4}\d{3}-[A-Z]{2}-\d{2}
   - Example: "PUAEQU002-DG-01"

2. **Scenario Types**
   - Must be one of: diagnostic, repair, maintenance, emergency

3. **Required Elements**
   - Minimum 2 elements per scenario
   - Must reference valid knowledge areas

4. **Steps Validation**
   - Minimum 3 steps per scenario
   - Maximum 5 steps per scenario
   - Each step must have:
     - Action description (string)
     - Points (integer 1-50)

5. **Difficulty Levels**
   - Must be one of: basic, intermediate, advanced

## Content Validation
1. **Scenario Description**
   - Minimum 20 characters
   - Maximum 200 characters
   - Must describe a clear scenario

2. **Point Allocation**
   - Total points must equal 100
   - No step can exceed 50 points

3. **Logical Flow**
   - Steps must follow logical sequence
   - No circular dependencies

## Implementation
```python
def validate_scenario(scenario):
    # Validate ID format
    if not re.match(r'^[A-Z]{2,4}\d{3}-[A-Z]{2}-\d{2}$', scenario['scenario_id']):
        return False
    
    # Validate type
    if scenario['type'] not in ['diagnostic', 'repair', 'maintenance', 'emergency']:
        return False
    
    # Validate steps
    if len(scenario['steps']) < 3 or len(scenario['steps']) > 5:
        return False
    
    # Validate points
    total_points = sum(step['points'] for step in scenario['steps'])
    if total_points != 100:
        return False
    
    return True