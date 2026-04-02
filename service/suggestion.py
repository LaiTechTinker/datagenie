def generate_suggestions(profile: dict, max_suggestions: int = 6):
    suggestions = []

    numeric_cols = profile["column_types"]["numeric"]
    categorical_cols = profile["column_types"]["categorical"]

    #  1. Aggregation suggestions
    for num in numeric_cols:
        for cat in categorical_cols:
            suggestions.append(f"Average {num} by {cat}")
            suggestions.append(f"Total {num} by {cat}")

    # 🔹 2. Count suggestions
    for cat in categorical_cols:
        suggestions.append(f"Count of records by {cat}")

    # 🔹 3. Distribution suggestions
    for num in numeric_cols:
        suggestions.append(f"Distribution of {num}")

    # Remove duplicates
    suggestions = list(dict.fromkeys(suggestions))

    # Limit suggestions
    return suggestions[:max_suggestions]