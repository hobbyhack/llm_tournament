# Response Validation

## Expected Format
$expected_format

## Actual Response
$response

## Task
Validate whether the response matches the expected format. If not, correct it to match the expected format while preserving the substantive content and evaluations.

Follow these instructions carefully:
1. Examine the actual response and compare it to the expected format
2. Identify any structural issues, missing fields, or formatting problems
3. If the response is valid, indicate this in your output
4. If the response is not valid, correct it to match the expected format while preserving the original assessment
5. If any critical information is missing and cannot be inferred, note this in your error message

## Response Format
You must respond with a JSON object in exactly the following format:

```json
{
  "is_valid": true,
  "corrected_response": {
    // The corrected response in the expected format
    // If is_valid is true, this should contain the original response
    // If is_valid is false, this should contain your corrected version
  },
  "error_message": "Detailed explanation of errors found and corrections made. Empty string if no errors."
}
```

Important notes:
- Preserve all substantive judgments and evaluations when correcting a response
- Do not change scores or winners unless necessary to fix structural issues
- Make sure all required fields are present in the corrected response
- Ensure all numeric values are properly formatted as numbers, not strings
- The corrected_response field should contain a complete, valid JSON object that matches the expected format
