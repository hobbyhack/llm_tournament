# Tournament Match Evaluation

## Assessment Framework
$framework_description

$formatted_criteria

$formatted_rules

$formatted_scoring

## Contenders

### Contender 1: $contender1_id
$contender1_content

### Contender 2: $contender2_id
$contender2_content

## Task
Evaluate these two contenders based on the assessment framework. Compare them directly against each other for each criterion.

Follow these instructions carefully:
1. Analyze each contender based on the criteria specified in the assessment framework
2. Compare the contenders directly against each other for each criterion
3. Assign a score for each criterion to each contender based on the scoring system
4. Calculate the overall scores using the weights defined in the criteria
5. Determine the winner based on the overall scores
6. Provide a detailed rationale for your evaluation
7. Format the response as a json object

## Response Format
You must respond with a JSON object in exactly the following format:

```json
{{
  "criteria_scores": {{
    "Criterion1Name": {{
      "contender1": 8.5,
      "contender2": 7.2
    }},
    "Criterion2Name": {{
      "contender1": 6.9,
      "contender2": 8.1
    }},
    ...additional criteria as needed
  }},
  "contender1_score": 7.8,
  "contender2_score": 7.5,
  "winner": "$contender1_id",
  "rationale": "Detailed explanation of the evaluation and comparison, highlighting strengths and weaknesses of each contender and justifying the scores and winner."
}}
```

Important notes:
- Use the exact criterion names as specified in the assessment framework
- Set the "winner" field to "$contender1_id", "$contender2_id", or null (for a tie)
- Calculate the overall score for each contender as the weighted sum of their criterion scores
- Scores should be within the range specified in the scoring system
- The "rationale" should provide a clear, detailed explanation of your evaluation
- Respond only with a json object.