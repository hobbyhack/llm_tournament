# Assessment Framework Generation Prompt

You will create a comprehensive assessment framework for evaluating <topic>. This framework will be used in a tournament-style evaluation system where contenders are systematically compared against each other using your criteria.

## Task

Research <topic> and develop a structured framework in JSON format that enables fair, consistent, and insightful evaluation. Your framework should define:

1. What makes something excellent in this domain
2. Clear criteria by which samples should be judged
3. Rules for conducting fair comparisons
4. A structured scoring system

## Framework Components

### ID and Description
Create a concise, descriptive ID and a thorough explanation of what this framework evaluates.

### Evaluation Criteria
Develop 3-5 distinct criteria that collectively capture the essential qualities of excellence in this domain. For each criterion:

- Use a clear, descriptive name (e.g., "Clarity" not "Quality 1")
- Write a detailed explanation of what this criterion measures
- Assign a weight (decimal between 0-1) reflecting its relative importance
- Ensure all weights sum to exactly 1.0

**Characteristics of effective criteria:**
- Mutually exclusive: Each measures something distinct
- Collectively exhaustive: Together they cover all important aspects
- Measurable: Can be evaluated objectively
- Relevant: Directly tied to meaningful outcomes
- Clear: Easily understood by evaluators

### Comparison Rules
Create 4-7 specific rules for how contenders should be compared. Rules should:

- Guide the evaluation process
- Address potential biases
- Set boundaries for what should/shouldn't be considered
- Establish how to handle edge cases

**Effective rules are:**
- Actionable: Provide clear guidance
- Specific: Address concrete scenarios
- Balanced: Promote fair evaluation
- Focused: Keep evaluators on the most important factors

### Scoring System
Define a structured scoring system with:
- Scale bounds (typically 0-10)
- Named categories within the scale (e.g., "Excellent" for 8-10)
- Clear descriptions of what each category represents

## Writing Style Guidelines

- **Be specific**: Avoid vague language like "good quality" - define what good means
- **Use precise language**: Choose words that have clear, unambiguous meanings
- **Be comprehensive**: Cover all relevant aspects of evaluation
- **Use technical terminology**: Incorporate domain-specific terms where appropriate
- **Maintain objectivity**: Focus on measurable qualities rather than subjective preferences
- **Be consistent**: Use parallel structure and consistent terminology throughout

## Response Format

Respond with a properly formatted JSON object matching this structure:

```json
{
  "assessment_framework": {
    "id": "domain-specific-framework-name",
    "description": "Detailed description of what this framework evaluates and why these criteria matter",
    "evaluation_criteria": [
      {
        "name": "Criterion1Name",
        "description": "Detailed explanation of this criterion",
        "weight": 0.35
      },
      {
        "name": "Criterion2Name",
        "description": "Detailed explanation of this criterion",
        "weight": 0.25
      },
      ... additional criteria with weights totaling exactly 1.0
    ],
    "comparison_rules": [
      "Specific rule guiding how to compare contenders",
      "Another specific rule for evaluation",
      ... additional rules
    ],
    "scoring_system": {
      "type": "points",
      "scale": {
        "min": 0,
        "max": 10
      },
      "categories": [
        {"name": "Excellent", "range": [8, 10], "description": "What excellent means for this domain"},
        {"name": "Good", "range": [6, 7.9], "description": "What good means for this domain"},
        ... additional categories
      ]
    }
  }
}
```

Ensure your JSON is valid with no syntax errors. Do not include any explanation or commentary outside the JSON structure.

## Example Weighting Approach

When assigning weights to criteria:
1. Identify which aspects are most fundamental to quality in this domain
2. Consider which criteria have the broadest impact
3. Allocate higher weights (e.g., 0.30-0.40) to the most critical criteria
4. Assign lower weights (e.g., 0.10-0.20) to supporting criteria
5. Verify weights sum to exactly 1.0

For example, in evaluating academic papers, "Methodological Rigor" might receive 0.35, "Novelty of Contribution" 0.25, "Clarity of Presentation" 0.25, and "Practical Implications" 0.15.

## Research Approach

1. Consider the core purpose of <topic>
2. Identify established standards or best practices
3. Consider multiple perspectives (creators, users, experts)
4. Identify common failure modes or shortcomings
5. Think about what distinguishes exceptional examples from merely adequate ones

Create a framework that is both technically precise and practically useful for evaluating <topic>.