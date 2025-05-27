# Scenario Generation Logic

## Scenario Types
1. **Diagnostic Scenarios** (Testing procedures)
2. **Repair Scenarios** (Fault resolution)
3. **Maintenance Scenarios** (Routine procedures)
4. **Emergency Scenarios** (Critical situations)

## Generation Rules

### Input Sources
- Knowledge Evidence requirements
- Performance Criteria
- Real-world case studies

### Template Structure
```
{
  "scenario_id": "PUAEQU002-DG-01",
  "type": "diagnostic",
  "description": "The pump fails to maintain pressure during operation",
  "required_elements": ["diagnostic_testing", "pressure_analysis"],
  "steps": [
    {"action": "Isolate fault", "points": 20},
    {"action": "Test system pressure", "points": 30},
    {"action": "Check for internal leakage", "points": 25}
  ],
  "difficulty": "intermediate"
}
```

### Difficulty Levels
1. **Basic**: Single fault, obvious symptoms
2. **Intermediate**: Multiple possible causes
3. **Advanced**: Complex systems with hidden faults

## Implementation

1. **Content Generation**:
```python
def generate_scenario(unit_data):
    # Select random knowledge evidence item
    # Map to performance criteria
    # Create plausible scenario text
    # Assign difficulty based on criteria complexity
    return scenario_object
```

2. **Validation Rules**:
- Must include at least 2 related Elements
- Must have 3-5 solution steps
- Points should sum to 100 per scenario

## Example LLM Prompts
1. "Generate a diagnostic scenario for pump pressure issues including 3 troubleshooting steps"
2. "Create an emergency scenario requiring quick diagnosis of foam system failure"
3. "Write a maintenance scenario covering routine pump inspection procedures"