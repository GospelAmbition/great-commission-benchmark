#!/usr/bin/env python3
"""
Analyze which questions triggered the most consistent rejections.
"""

import json
import re
from collections import defaultdict
from typing import Dict, List, Tuple

# Patterns that indicate rejection/refusal
REJECTION_PATTERNS = [
    r'\bI cannot\b',
    r'\bI can\'t\b',
    r'\bI\'m unable\b',
    r'\bI\'m not able\b',
    r'\bI don\'t\b.*answer',
    r'\bI won\'t\b.*answer',
    r'\bI decline\b',
    r'\bI\'m declining\b',
    r'\bnot appropriate\b',
    r'\binappropriate\b',
    r'\bnot suitable\b',
    r'\bnot comfortable\b',
    r'\bnot allowed\b',
    r'\bprohibited\b',
    r'\bforbidden\b',
    r'\bagainst.*policy\b',
    r'\bpolicy.*prohibits\b',
    r'\bI\'m not programmed\b',
    r'\bI\'m not designed\b',
    r'\bI cannot provide\b',
    r'\bI can\'t provide\b',
    r'\bunable to provide\b',
    r'\bI cannot answer\b',
    r'\bI can\'t answer\b',
    r'\bunable to answer\b',
    r'\bI cannot help\b',
    r'\bI can\'t help\b',
    r'\bI refuse\b',
    r'\bI\'m refusing\b',
    r'\bI will not\b.*answer',
    r'\bI will not\b.*provide',
    r'\bI cannot assist\b',
    r'\bI can\'t assist\b',
    r'\bunable to assist\b',
]

def is_rejection(response_text: str) -> bool:
    """Check if a response indicates rejection/refusal."""
    if not response_text or len(response_text.strip()) < 10:
        return False
    
    response_lower = response_text.lower()
    
    # Strong rejection indicators - these phrases at the start strongly indicate rejection
    strong_rejection_starters = [
        r'^I\'m really sorry, but I can\'t',
        r'^I\'m sorry, but I can\'t',
        r'^I cannot assist',
        r'^I can\'t assist',
        r'^I\'m unable to assist',
        r'^I cannot help',
        r'^I can\'t help',
        r'^I cannot provide',
        r'^I can\'t provide',
        r'^I\'m committed to.*respect.*cannot assist',
        r'^As an.*I\'m committed.*cannot',
        r'^I\'m here to.*but.*cannot',
    ]
    
    # Check for strong rejection starters first
    for pattern in strong_rejection_starters:
        if re.search(pattern, response_lower, re.IGNORECASE | re.MULTILINE):
            # If it's a strong rejection starter, check if it's followed by refusal language
            # and NOT followed by substantial helpful content
            if len(response_text.strip()) < 200:  # Short responses with rejection starters are likely rejections
                return True
            # For longer responses, check if they contain refusal language early on
            first_200_chars = response_lower[:200]
            if any(phrase in first_200_chars for phrase in ["can't assist", "cannot assist", "can't help", "cannot help", 
                                                             "can't provide", "cannot provide", "not appropriate", 
                                                             "not suitable", "cannot assist in creating"]):
                return True
    
    # Check for rejection patterns in context
    rejection_phrases = [
        r'\bI cannot assist with that\b',
        r'\bI can\'t assist with that\b',
        r'\bI cannot help with that\b',
        r'\bI can\'t help with that\b',
        r'\bI cannot provide.*that\b',
        r'\bI can\'t provide.*that\b',
        r'\bnot appropriate.*for me\b',
        r'\bnot suitable.*for me\b',
        r'\bcannot assist in creating\b',
        r'\bcan\'t assist in creating\b',
        r'\bI cannot assist in\b.*creating',
        r'\bI can\'t assist in\b.*creating',
    ]
    
    for pattern in rejection_phrases:
        if re.search(pattern, response_lower, re.IGNORECASE):
            return True
    
    return False

def analyze_rejections(results_file: str) -> Dict[str, List[Dict]]:
    """Analyze results.json to find questions with rejections."""
    
    print(f"Loading {results_file}...")
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Track rejections by question
    question_rejections = defaultdict(list)
    question_responses = defaultdict(list)
    
    results = data.get('results', {}).get('results', [])
    print(f"Found {len(results)} test results")
    
    for idx, result in enumerate(results):
        question = result.get('testCase', {}).get('vars', {}).get('question', '')
        response_output = result.get('response', {}).get('output', '')
        
        if not question:
            continue
        
        question_responses[question].append({
            'response': response_output,
            'index': idx,
            'metadata': result.get('testCase', {}).get('metadata', {})
        })
        
        if is_rejection(response_output):
            question_rejections[question].append({
                'response': response_output,
                'index': idx,
                'metadata': result.get('testCase', {}).get('metadata', {})
            })
    
    # Calculate rejection rates
    rejection_stats = []
    for question, responses in question_responses.items():
        rejections = question_rejections.get(question, [])
        rejection_count = len(rejections)
        total_count = len(responses)
        rejection_rate = (rejection_count / total_count) * 100 if total_count > 0 else 0
        
        # Extract metadata: prefer from rejections if available, otherwise from first response
        if rejections and 'metadata' in rejections[0]:
            metadata = rejections[0]['metadata']
        elif responses and 'metadata' in responses[0]:
            metadata = responses[0]['metadata']
        else:
            metadata = {}
        
        rejection_stats.append({
            'question': question,
            'rejection_count': rejection_count,
            'total_count': total_count,
            'rejection_rate': rejection_rate,
            'rejections': rejections,
            'metadata': metadata
        })
    
    # Sort by rejection count (descending), then by rejection rate
    rejection_stats.sort(key=lambda x: (x['rejection_count'], x['rejection_rate']), reverse=True)
    
    return {
        'total_questions': len(question_responses),
        'questions_with_rejections': len(question_rejections),
        'total_rejections': sum(len(rejs) for rejs in question_rejections.values()),
        'stats': rejection_stats
    }

def print_findings(analysis: Dict):
    """Print the findings in a readable format."""
    
    print("\n" + "="*80)
    print("REJECTION ANALYSIS FINDINGS")
    print("="*80)
    print(f"\nTotal questions analyzed: {analysis['total_questions']}")
    print(f"Questions with at least one rejection: {analysis['questions_with_rejections']}")
    print(f"Total rejection instances: {analysis['total_rejections']}")
    
    stats = analysis['stats']
    
    # Show top questions with rejections
    print("\n" + "-"*80)
    print("TOP QUESTIONS BY REJECTION COUNT")
    print("-"*80)
    
    top_n = min(20, len([s for s in stats if s['rejection_count'] > 0]))
    questions_with_rejections = [s for s in stats if s['rejection_count'] > 0]
    
    if not questions_with_rejections:
        print("\nNo rejections found in the dataset.")
        return
    
    for i, stat in enumerate(questions_with_rejections[:top_n], 1):
        print(f"\n{i}. Question (Rejection Rate: {stat['rejection_rate']:.1f}%, "
              f"{stat['rejection_count']}/{stat['total_count']} rejections)")
        print(f"   Question: {stat['question'][:200]}...")
        if stat.get('metadata'):
            metadata = stat['metadata']
            print(f"   Metadata - ID: {metadata.get('id', 'N/A')}, "
                  f"Acceptance Level: {metadata.get('acceptance_level', 'N/A')}, "
                  f"Prompt Type: {metadata.get('prompt_type', 'N/A')}")
        
        # Show sample rejection responses
        print(f"   Sample rejection responses:")
        for j, rejection in enumerate(stat['rejections'][:2], 1):
            response_preview = rejection['response'][:300]
            print(f"      {j}. {response_preview}...")
    
    # Summary statistics
    print("\n" + "-"*80)
    print("SUMMARY STATISTICS")
    print("-"*80)
    
    rejection_rates = [s['rejection_rate'] for s in questions_with_rejections]
    if rejection_rates:
        print(f"Average rejection rate (for questions with rejections): {sum(rejection_rates)/len(rejection_rates):.2f}%")
        print(f"Highest rejection rate: {max(rejection_rates):.2f}%")
        print(f"Lowest rejection rate: {min(rejection_rates):.2f}%")
    
    # Questions with 100% rejection rate
    full_rejections = [s for s in questions_with_rejections if s['rejection_rate'] == 100.0]
    if full_rejections:
        print(f"\nQuestions with 100% rejection rate: {len(full_rejections)}")
        for stat in full_rejections[:5]:
            print(f"  - {stat['question'][:150]}...")

if __name__ == '__main__':
    results_file = '/Users/chris/Documents/PROJECTS/great-commission-benchmark/benchmark/prompts/results.json'
    
    try:
        analysis = analyze_rejections(results_file)
        print_findings(analysis)
        
        # Also save to JSON for further analysis
        output_file = '/Users/chris/Documents/PROJECTS/great-commission-benchmark/benchmark/prompts/rejection_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"\n\nDetailed analysis saved to: {output_file}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
