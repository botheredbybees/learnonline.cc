# Card Data Model

## Card Types
1. **Element Card**
   - Title (string)
   - Description (string)
   - Related Knowledge (string)
   - Example (string)

2. **Performance Card**
   - Action (string)
   - Required Element (string)
   - Scoring Weight (integer)
   - Example (string)

3. **Scenario Card**
   - Scenario Text (string)
   - Expected Elements (string)
   - Solution Steps (string)
   - Difficulty (string)

## Data Structure
```json
{
  "card_type": "element",
  "title": "Diagnostic Testing",
  "description": "Testing procedures for pump systems",
  "related_knowledge": "Pressure analysis, flow measurement",
  "example": "Test system pressure"
}
```

## Validation Rules
- Title: 3-50 characters
- Description: 10-200 characters
- Related Knowledge: 5-100 characters
- Example: 5-100 characters