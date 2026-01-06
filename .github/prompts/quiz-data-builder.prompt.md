---
agent: agent
---

# Detailed Instructions: Converting quiz-reference-json to quiz-data-json Format

## Overview

The conversion process transforms a structured quiz database from quiz-reference-json into the #file:game.json format pattern used by the quiz-data-json file. This transformation involves restructuring the JSON schema, reorganizing answer options, and ensuring compatibility with the game's quiz engine. The primary goal is to convert from an array-based educational format into a numbered object-based gaming format while maintaining data integrity and creating a balanced, non-obvious answer distribution for multiple-choice questions.

## Step 1: Understanding the Source Structure

The source file (quiz-reference-json) contains quiz data organized as an array of question objects within a "summary" property. Each question object includes several key fields that describe the question, its correct answer(s), incorrect options, and educational context. Before beginning the conversion, you need to understand these components:

- **item-number**: A string identifier like "01", "02", etc., representing the question number
- **question**: The full text of the question being asked
- **correct-answer**: An array containing one or more correct answers (single-item array for single-answer questions, multiple items for multiple-answer questions)
- **answer-type**: Either "single" or "multiple", indicating whether the question requires one correct answer or multiple correct answers
- **options**: An array of incorrect answer choices
- **answer-explanation**: Detailed explanation of why the correct answer is right and why other options are wrong
- **answer-explanation-link**: A URL pointing to Microsoft Learn documentation for further reading

## Step 2: Understanding the Target Structure

The target file (quiz-data-json) follows the #file:game.json pattern where questions are organized as numbered object keys rather than an array. The structure is simpler and optimized for game logic:

- Questions are stored as direct properties with numeric string keys ("1", "2", "3", etc.)
- Each question object contains three main properties:
  - **question**: The question text
  - **description**: The answer explanation
  - **textAnswer**: An object with exactly 4 numbered options ("1", "2", "3", "4")
- The game engine expects option "1" to always be the correct answer
- All four options must be present for the game interface to work properly

## Step 3: Performing the Basic Conversion

Begin by restructuring the overall JSON format. Remove the "summary" array wrapper and create a root object with numbered keys:

- Convert item-number "01" to key "1"
- Convert item-number "02" to key "2"
- Continue this pattern for all 50 questions, removing leading zeros

For each question, map the fields directly:

- Copy the **question** field as-is to the new structure
- Copy the **answer-explanation** field directly to the **description** field
  - This provides learners with immediate context about why the answer is correct

## Step 4: Converting Single-Answer Questions

For questions where answer-type equals "single", the conversion is straightforward because there is only one correct answer and three incorrect options:

- **Option 1** (textAnswer["1"]): Extract the first (and only) item from the correct-answer array
  - This becomes the correct answer that the game will check against user selection
  
- **Option 2** (textAnswer["2"]): Take the first item from the options array
  - This is the first incorrect choice
  
- **Option 3** (textAnswer["3"]): Take the second item from the options array
  - This is the second incorrect choice
  
- **Option 4** (textAnswer["4"]): Take the third item from the options array
  - This is the third incorrect choice

Example transformation:
```json
Source: 
{
  "correct-answer": ["Azure AI Document Intelligence"],
  "options": ["Azure Metrics Advisor", "Azure Application Insights", "Azure AI Language"]
}
        
Target: 
{
  "textAnswer": {
    "1": "Azure AI Document Intelligence",
    "2": "Azure Metrics Advisor",
    "3": "Azure Application Insights",
    "4": "Azure AI Language"
  }
}
```

## Step 5: Converting Multiple-Answer Questions (Initial Pass)

Multiple-answer questions require special handling because they have more than one correct answer. The initial approach combines all correct answers into option 1:

- **Option 1** (textAnswer["1"]): Join all items from the correct-answer array with comma-space separators
  - For a question with three correct answers: `correctAnswer[0] + ", " + correctAnswer[1] + ", " + correctAnswer[2]`
  - This creates a single string containing all correct answers
  - Example: "Conduct red team exercises to test vulnerabilities., Document the model's decision-making logic., Integrate Azure AI Foundry Content Safety APIs."

At this stage, options 2, 3, and 4 would simply contain the incorrect choices from the options array, but this creates an obvious problem.

## Step 6: Balancing Multiple-Answer Questions (Final Pass)

The critical issue with the initial approach is that option 1 becomes obviously correct because it's the only option with multiple comma-separated items. To create a fair, challenging quiz experience, all four options must contain multiple items. This is achieved by mixing correct and incorrect answers in options 2, 3, and 4:

- **Option 2** (textAnswer["2"]): 
  - Start with the first incorrect option (options[0])
  - Append correct answers from indices 1 and 2
  - Format: `options[0] + ", " + correctAnswer[1] + ", " + correctAnswer[2]`
  - This creates a plausible but incorrect combination

- **Option 3** (textAnswer["3"]):
  - Start with the second incorrect option (options[1])
  - Append correct answers from indices 2 and 0 (rotated order)
  - Format: `options[1] + ", " + correctAnswer[2] + ", " + correctAnswer[0]`
  - The rotation ensures variety in answer distribution

- **Option 4** (textAnswer["4"]):
  - Start with the third incorrect option (options[2])
  - Append correct answers from indices 0 and 1
  - Format: `options[2] + ", " + correctAnswer[0] + ", " + correctAnswer[1]`
  - Different ordering prevents pattern recognition

The key principle is that each incorrect option contains:
- Exactly one incorrect answer (at the beginning)
- Two correct answers (appended after)
- This maintains the same visual pattern as option 1, making it impossible to guess the correct answer based on format alone

Example for a three-correct-answer question:
```json
Source: 
{
  "correct-answer": ["Red team exercises", "Document logic", "Content Safety APIs"],
  "options": ["User feedback", "Synthetic data", "Sandbox only"]
}

Target: 
{
  "textAnswer": {
    "1": "Red team exercises, Document logic, Content Safety APIs",
    "2": "User feedback, Document logic, Content Safety APIs",
    "3": "Synthetic data, Content Safety APIs, Red team exercises",
    "4": "Sandbox only, Red team exercises, Document logic"
  }
}
```

## Step 7: Quality Assurance Checks

After completing the conversion, verify the following requirements:

- **Structural integrity**: Every question must have exactly 4 textAnswer options numbered "1" through "4"
- **Correct answer placement**: Option "1" always contains only correct answers and nothing else
- **Multiple-answer consistency**: For multiple-answer questions, all 4 options must contain the same number of comma-separated items
- **Description completeness**: Every description field contains the answer explanation
- **JSON validity**: The entire file must be valid JSON with proper comma placement, bracket matching, and quote escaping
- **Question numbering**: All questions are numbered consecutively from "1" to "50" without gaps or duplicates
- **Text preservation**: Question text remains unchanged and complete, with no truncation or modification

## Summary of Key Transformations

The conversion process achieves the following transformations:

- **Schema change**: Array-based structure → Object-based structure with numeric keys
- **Field mapping**: answer-explanation → description field
- **Answer normalization**: Variable-length correct-answer arrays → Fixed 4-option format with correct answer always in position 1
- **Multiple-answer balancing**: Single-item incorrect options → Multi-item options that mirror the correct answer's format
- **Index conversion**: String item-numbers with leading zeros → Numeric string keys without leading zeros

This systematic approach ensures that the converted quiz data maintains educational integrity while being optimized for the game engine's requirements and providing a fair, challenging user experience.

## Visual Comparison

### Before (quiz-reference-json):
```json
{
  "summary": [
    {
      "item-number": "01",
      "question": "You are building an app...",
      "correct-answer": ["Azure AI Document Intelligence"],
      "answer-type": "single",
      "options": ["Azure Metrics Advisor", "Azure Application Insights", "Azure AI Language"],
      "answer-explanation": "Azure AI Document Intelligence is capable...",
      "answer-explanation-link": "https://learn.microsoft.com/..."
    }
  ]
}
```

### After (quiz-data-json):
```json
{
  "1": {
    "question": "You are building an app...",
    "description": "Azure AI Document Intelligence is capable...",
    "textAnswer": {
      "1": "Azure AI Document Intelligence",
      "2": "Azure Metrics Advisor",
      "3": "Azure Application Insights",
      "4": "Azure AI Language"
    }
  }
}
```

## Notes for Developers

- This conversion can be automated using scripts in Python, JavaScript, or any language with JSON parsing capabilities
- Pay special attention to escape characters in strings, especially in question text that may contain quotes
- The comma-space separator (", ") is critical for maintaining consistency across all multiple-answer options
- Always validate the output JSON file before deploying to ensure the game engine can parse it correctly
- Consider creating a validation script that checks all the quality assurance requirements automatically
