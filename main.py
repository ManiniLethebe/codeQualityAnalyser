# Code Quality Analyzer
import difflib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast
import re


def analyze_code_complexity(code):
    # Analyzes the complexity of the code based on the number of commented lines.
    complexity_score = 0

    for line in code.split("\n"):
        if line.strip().startswith("#"):
            complexity_score += 1

    return complexity_score


def analyze_code_quality(code):

    # Analyzes the overall quality of the code based on complexity and common coding mistakes.

    quality_score = 0

    complexity_score = analyze_code_complexity(code)
    quality_score += complexity_score

    if "goto" in code:
        quality_score -= 10
    if "magic_number" in code:
        quality_score -= 5

    return quality_score


def calculate_average_function_length(tree):
    # Calculates the average length of functions in the code based on the abstract syntax tree (AST).

    function_lengths = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_lengths.append(len(node.body))

    average_length = sum(function_lengths) / len(function_lengths) if function_lengths else 0

    return average_length


def check_naming_conventions(tree):
    # Checks the naming conventions of variables and functions in the code.

    violations = []
    modified_code = None

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            if not function_name.islower():
                violations.append(f"Function name '{function_name}' should be in lowercase.")
                # Modify the function name to lowercase
                node.name = function_name.lower()
                modified_code = compile(tree, filename='', mode='exec')
        elif isinstance(node, ast.Name):
            variable_name = node.id
            if variable_name.isupper():
                violations.append(f"Variable name '{variable_name}' should not be in uppercase.")
                # Modify the variable name to lowercase
                node.id = variable_name.lower()
                modified_code = compile(tree, filename='', mode='exec')
            elif not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', variable_name):
                violations.append(f"Variable name '{variable_name}' does not follow naming conventions.")

    return violations, modified_code


def recommend_coding_style(code):
    # Recommends coding style improvements based on code analysis.
    # and provides recommendations for coding style improvements.

    tree = ast.parse(code)
    recommendations = []
    modified_code = code

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            if not ast.get_docstring(node):
                if isinstance(node, ast.FunctionDef):
                    line_number = node.body[0].lineno
                    if code.split("\n")[line_number - 1].strip().startswith("#"):
                        continue  # Skip if the line is already commented
                    recommendations.append(f"Consider adding comments to function '{node.name}'.")
                    modified_code = modified_code[
                                    :line_number - 1] + f"\n# Add comments here\n" + modified_code[
                                                                                                   line_number - 1:]
                elif isinstance(node, ast.ClassDef):
                    line_number = node.body[0].lineno
                    if code.split("\n")[line_number - 1].strip().startswith("#"):
                        continue  # Skip if the line is already commented
                    recommendations.append(f"Consider adding comments to class '{node.name}'.")
                    modified_code = modified_code[
                                    :line_number - 1] + f"\n# Add comments here\n" + modified_code[
                                                                                                   line_number - 1:]
                elif isinstance(node, ast.Module):
                    if code.split("\n")[0].strip().startswith("#"):
                        continue  # Skip if the line is already commented
                    recommendations.append("Consider adding comments here.")
                    modified_code = f"# Add comments here\n" + modified_code

    # Check for line length
    line_length_limit = 79
    lines = code.split("\n")
    for i, line in enumerate(lines, start=1):
        if len(line) > line_length_limit:
            recommendations.append(f"Consider splitting line {i} as it exceeds the line length limit of {line_length_limit} characters.")
            modified_code = modified_code[:i-1] + "\\\n" + modified_code[i:]

    if not recommendations:
        recommendations.append("No coding style recommendations found.")
        modified_code = "No modified actions applied"

    for recommendation in recommendations:
        print("Recommended coding style: ")
        print(recommendation)

    return recommendations, modified_code

def analyze_code(code):

    # Analyzes the code for complexity, quality, duplication, naming conventions, design patterns,
    # and provides recommendations for coding style improvements.

    result = {}

    result['complexity_score'] = analyze_code_complexity(code)
    result['quality_score'] = analyze_code_quality(code)

    tree = ast.parse(code)
    result['average_function_length'] = calculate_average_function_length(tree)

    result['naming_violations'] = check_naming_conventions(tree)
    result['recommendations'] = recommend_coding_style(code)

    return result


def detect_repeated_code(code):
    lines = code.split('\n')
    repeated_code = []

    for i, line1 in enumerate(lines):
        for j, line2 in enumerate(lines[i+1:]):
            similarity = difflib.SequenceMatcher(None, line1, line2).ratio()

            if similarity > 0.8:
                repeated_code.append((i, j+i+1))

    return repeated_code


if __name__ == "__main__":
    code = input("Enter your code for analysis: ").strip()

    while not code:
        print("Empty input! Please provide code.")
        code = input("Enter your code for analysis: ").strip()

    try:
        analysis_results = analyze_code(code)
    except SyntaxError as e:
        print("Invalid syntax in the provided code.")
        print(e)
        exit(1)

    print("Code Complexity Score:", analysis_results['complexity_score'])
    print("Code Quality Score:", analysis_results['quality_score'])
    # print("Code Duplication Percentage:", analysis_results['duplication_percentage'])
    print("Average Function Length:", analysis_results['average_function_length'])

    # Additional code from the provided code
    recommendations, modified_code = analysis_results['recommendations']
    # recommendations, modified_code = recommend_coding_style(code)
    print("Modified Code:")
    print(modified_code)

    tree = ast.parse(code)
    naming_violations, modified_code = check_naming_conventions(tree)

    for violation in naming_violations:
        print("Naming convention violation identified: ")
        print(violation)
        break
    else:
        print("Naming convention violation identified: ")
        print("No naming convention violation identified")

    scores = [analysis_results['quality_score'], 20, 10, 15, 5]
    sorted_scores = sorted(scores, reverse=True)
    print("Sorted Scores:", sorted_scores)

    repeated_code = detect_repeated_code(code)
    if repeated_code:
        print("Repeated Code:")
        for i, j in repeated_code:
            print(f"lines {i+1} and {j+1}")
    else:
        print("No repeated code found.")

    data = {
        'Code Sample': ['A', 'B', 'C', 'D', 'E'],
        'Quality Score': sorted_scores
    }
    df = pd.DataFrame(data)

    mean_score = df['Quality Score'].mean()
    max_score = df['Quality Score'].max()
    min_score = df['Quality Score'].min()

    print("Mean Score:", mean_score)
    print("Max Score:", max_score)
    print("Min Score:", min_score)

    sample_names = df['Code Sample'].tolist()
    quality_scores = df['Quality Score'].tolist()
    sample_dict = df.to_dict()

    sample_names_upper = [name.upper() for name in sample_names]
    score_dict = {name: score for name, score in zip(sample_names, quality_scores)}

    print("Sample Names (Upper):", sample_names_upper)
    print("Score Dictionary:", score_dict)
    print("DataFrame as Dictionary:", sample_dict)

    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    quality_scores = np.random.randint(1, 100, size=len(days))
    recommended_style = np.random.randint(1, 100, size=len(days))
    naming_violations = np.random.randint(1, 100, size=len(days))
    duplicate_code = np.random.randint(1, 100, size=len(days))
    modified_code = np.random.randint(1, 100, size=len(days))

    # Create a DataFrame
    df = pd.DataFrame({
        'Day': days,
        'Quality Score': quality_scores,
        'Recommended Style': recommended_style,
        'Naming Violations': naming_violations,
        'Duplicate Code': duplicate_code,
        'Modified Code': modified_code
    })

    # Sort the DataFrame by year in ascending order
    df.sort_values('Day', inplace=True)

    # Set distinct and clearer colors for the bars
    colors = ['#FFC300', '#FF5733', '#C70039', '#900C3F', '#581845']

    # Create the bar plot
    plt.figure(figsize=(10, 6))

    bar_width = 0.14
    index = np.arange(len(df['Day']))

    plt.bar(index, df['Quality Score'], width=bar_width, color=colors[0], label='Quality Score')
    plt.bar(index + bar_width, df['Recommended Style'], width=bar_width, color=colors[1], label='Recommended Style')
    plt.bar(index + 2 * bar_width, df['Naming Violations'], width=bar_width, color=colors[2], label='Naming Violations')
    plt.bar(index + 3 * bar_width, df['Duplicate Code'], width=bar_width, color=colors[3], label='Duplicate Code')
    plt.bar(index + 4 * bar_width, df['Modified Code'], width=bar_width, color=colors[4], label='Modified Code')

    # Set the labels and title
    plt.xlabel('Day')
    plt.ylabel('Metrics')
    plt.title('Code Quality Metrics Over Time')
    plt.xticks(index + 2 * bar_width, df['Day'])
    plt.legend()

    # Display the plot
    plt.tight_layout()
    plt.show()

    sample_set = set(sample_names)
    unique_samples = {'F', 'G', 'H'}

    union_set = sample_set.union(unique_samples)
    print("Union Set:", union_set)

    intersection_set = sample_set.intersection(unique_samples)
    print("Intersection Set:", intersection_set)

    difference_set = sample_set.difference(unique_samples)
    print("Difference Set:", difference_set)
