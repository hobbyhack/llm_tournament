# Scoring Evaluation

## Scoring System
$formatted_scoring

## Evaluation
$evaluation

## Task
Based on the provided evaluation, assign scores according to the scoring system. Your task is to convert the qualitative evaluation into quantitative scores that align with the scoring system.

Follow these instructions carefully:
1. Read the evaluation carefully to understand the performance of each contender on each criterion
2. Assign a numeric score for each criterion based on the scoring system
3. Calculate weighted scores using the weights specified in the criteria
4. Determine the overall winner based on the total weighted scores
5. Ensure your scores are consistent with the evaluation text

## Response Format
You must respond with a JSON object in exactly the following format:

```json
{
  "scores": {
    "CriterionName": {
      "contender1": 8.5,
      "contender2": 7.2
    },
    "AnotherCriterionName": {
      "contender1": 6.9,
      "contender2": 8.1
    },
    ...additional criteria as needed
  },
  "overall_scores": {
    "contender1": 7.8,
    "contender2": 7.5
  },
  "winner": "contender1_id"
}
```

Important notes:
- Scores should be within the range specified in the scoring system
- The overall scores should be calculated as weighted averages using the criteria weights
- The "winner" field should contain the ID of the contender with the highest overall score, or null if tied
- Scores should accurately reflect the nuances described in the evaluation text
