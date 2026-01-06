#!/usr/bin/env python3
"""
Quiz Data Converter
Converts quiz data from ai-engr1.json format to ai-engr.json (game.json) format.

Usage:
    python convert_quiz_data.py <input_file> <output_file>
    python convert_quiz_data.py data/ai-engr1.json data/ai-engr.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def convert_single_answer_question(correct_answer: List[str], options: List[str]) -> Dict[str, str]:
    """
    Convert a single-answer question to the game format.
    
    Args:
        correct_answer: List containing one correct answer
        options: List of incorrect answer options
        
    Returns:
        Dictionary with 4 numbered text answers
    """
    return {
        "1": correct_answer[0],
        "2": options[0] if len(options) > 0 else "",
        "3": options[1] if len(options) > 1 else "",
        "4": options[2] if len(options) > 2 else ""
    }


def convert_multiple_answer_question(correct_answer: List[str], options: List[str]) -> Dict[str, str]:
    """
    Convert a multiple-answer question to the game format.
    All 4 options will have multiple items to avoid obvious correct answer.
    
    Args:
        correct_answer: List containing multiple correct answers
        options: List of incorrect answer options
        
    Returns:
        Dictionary with 4 numbered text answers, each containing multiple items
    """
    # Option 1: All correct answers joined with comma-space
    option_1 = ", ".join(correct_answer)
    
    # For options 2, 3, 4: Mix incorrect option with some correct answers
    # This makes all options appear similar in format
    
    # Option 2: First incorrect + correct answers from index 1 onwards
    if len(correct_answer) >= 2:
        option_2_parts = [options[0]] + correct_answer[1:] if len(options) > 0 else correct_answer
    else:
        option_2_parts = [options[0]] if len(options) > 0 else correct_answer
    option_2 = ", ".join(option_2_parts)
    
    # Option 3: Second incorrect + correct answers rotated (from index 2, then 0, etc.)
    if len(correct_answer) >= 2:
        rotated_correct = correct_answer[2:] + correct_answer[:2] if len(correct_answer) > 2 else [correct_answer[-1], correct_answer[0]]
        option_3_parts = [options[1]] + rotated_correct if len(options) > 1 else rotated_correct
    else:
        option_3_parts = [options[1]] if len(options) > 1 else correct_answer
    option_3 = ", ".join(option_3_parts)
    
    # Option 4: Third incorrect + correct answers from beginning
    if len(correct_answer) >= 2:
        option_4_parts = [options[2]] + correct_answer[:len(correct_answer)-1] if len(options) > 2 else correct_answer[:len(correct_answer)-1]
    else:
        option_4_parts = [options[2]] if len(options) > 2 else correct_answer
    option_4 = ", ".join(option_4_parts)
    
    return {
        "1": option_1,
        "2": option_2,
        "3": option_3,
        "4": option_4
    }


def convert_question(question_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a single question from source format to target format.
    
    Args:
        question_data: Question data in ai-engr1.json format
        
    Returns:
        Question data in ai-engr.json format
    """
    question_text = question_data.get("question", "")
    correct_answer = question_data.get("correct-answer", [])
    answer_type = question_data.get("answer-type", "single")
    options = question_data.get("options", [])
    explanation = question_data.get("answer-explanation", "")
    # explanation_link = question_data.get("answer-explanation-link", "")
    
    # Create description by combining explanation and link
    description = explanation
    # if explanation_link:
    #     description += f" Learn more: {explanation_link}"
    
    # Convert text answers based on answer type
    if answer_type == "single":
        text_answer = convert_single_answer_question(correct_answer, options)
    else:  # multiple
        text_answer = convert_multiple_answer_question(correct_answer, options)
    
    return {
        "question": question_text,
        "description": description,
        "textAnswer": text_answer
    }


def convert_quiz_data(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert entire quiz data from source format to target format.
    
    Args:
        input_data: Full quiz data in ai-engr1.json format
        
    Returns:
        Full quiz data in ai-engr.json format
    """
    summary = input_data.get("summary", [])
    output_data = {}
    
    for question_data in summary:
        # Get item number and convert to numeric string key (remove leading zeros)
        item_number = question_data.get("item-number", "")
        numeric_key = str(int(item_number))
        
        # Convert the question
        converted_question = convert_question(question_data)
        output_data[numeric_key] = converted_question
    
    return output_data


def validate_output(output_data: Dict[str, Any]) -> List[str]:
    """
    Validate the converted output data.
    
    Args:
        output_data: Converted quiz data
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    for key, question in output_data.items():
        # Check required fields
        if "question" not in question:
            errors.append(f"Question {key}: Missing 'question' field")
        if "description" not in question:
            errors.append(f"Question {key}: Missing 'description' field")
        if "textAnswer" not in question:
            errors.append(f"Question {key}: Missing 'textAnswer' field")
            continue
        
        text_answer = question["textAnswer"]
        
        # Check that exactly 4 options exist
        if len(text_answer) != 4:
            errors.append(f"Question {key}: Expected 4 textAnswer options, got {len(text_answer)}")
        
        # Check that options are numbered 1-4
        required_keys = {"1", "2", "3", "4"}
        if set(text_answer.keys()) != required_keys:
            errors.append(f"Question {key}: textAnswer keys must be '1', '2', '3', '4'")
        
        # For questions with multiple items in option 1, check all options have multiple items
        if "1" in text_answer and ", " in text_answer["1"]:
            for option_key in ["2", "3", "4"]:
                if option_key in text_answer and ", " not in text_answer[option_key]:
                    errors.append(f"Question {key}: Option {option_key} should have multiple items like option 1")
    
    return errors


def main():
    """Main function to handle command-line conversion."""
    if len(sys.argv) != 3:
        print("Usage: python convert_quiz_data.py <input_file> <output_file>")
        print("Example: python convert_quiz_data.py data/ai-engr1.json data/ai-engr.json")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    # Check if input file exists
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    # Read input file
    print(f"Reading input file: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    # Convert the data
    print("Converting quiz data...")
    output_data = convert_quiz_data(input_data)
    
    # Validate output
    print("Validating converted data...")
    errors = validate_output(output_data)
    
    if errors:
        print("\nValidation errors found:")
        for error in errors:
            print(f"  - {error}")
        print(f"\nTotal errors: {len(errors)}")
        
        response = input("\nContinue with conversion despite errors? (y/N): ")
        if response.lower() != 'y':
            print("Conversion cancelled.")
            sys.exit(1)
    else:
        print("Validation passed!")
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output file
    print(f"Writing output file: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)
    
    print("\n✓ Conversion complete!")
    print(f"  Questions converted: {len(output_data)}")
    print(f"  Output saved to: {output_file}")


if __name__ == "__main__":
    main()
