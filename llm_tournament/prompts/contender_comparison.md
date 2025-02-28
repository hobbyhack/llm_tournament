# Contender Comparison

## Criteria
$formatted_criteria

## Contenders

### Contender 1: $contender1_id
$contender1_content

### Contender 2: $contender2_id
$contender2_content

## Task
Compare these two contenders directly against each other using the provided criteria. For each criterion, determine which contender is stronger and explain why.

Follow these instructions carefully:
1. Consider each criterion separately and make a direct comparison
2. Identify the strengths and weaknesses of each contender for each criterion
3. Determine which contender is stronger overall, based on the weighted importance of the criteria
4. Provide a detailed justification for your conclusion

## Response Format
You must respond with a JSON object in exactly the following format:

```json
{{
  "comparisons": [
    {{
      "criterion": "CriterionName",
      "winner": "$contender1_id",
      "explanation": "Detailed explanation of why contender 1 is stronger for this criterion"
    }},
    {{
      "criterion": "AnotherCriterionName",
      "winner": "$contender2_id",
      "explanation": "Detailed explanation of why contender 2 is stronger for this criterion"
    }},
    ...additional criteria as needed
  ],
  "overall_winner": "$contender1_id",
  "rationale": "Comprehensive explanation of the overall comparison, synthesizing the individual criterion comparisons and weighing them according to the specified weights."
}}
```

Important notes:
- Use the exact criterion names as specified
- Set the "winner" field for each criterion to "$contender1_id", "$contender2_id", or null (if tied)
- Set the "overall_winner" field to "$contender1_id", "$contender2_id", or null (if tied)
- The overall winner should be determined by considering the weights of the criteria
- The "rationale" should provide a thorough explanation of your overall assessment