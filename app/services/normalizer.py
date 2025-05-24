import re

merchant_app = {
    "JUMIA": "Jumia",
    "SPAR": "Spar Supermarket",
    "CHICKEN REPUBLIC": "Chicken Republic",
    "POS": "POS Withdrawal",
    "NETFLIX": "Netflix",
    "DSTV": "DStv Subscription",
}

category_rules = {
    "food & frink": [
        "JUMIA",
        "SPAR",
        "CHICKEN REPUBLIC",
        "KFC",
        "DOMINO'S PIZZA",
        "PIZZA HUT",
        "FOOD COURT",
    ],
    "entertainment": ["NETFLIX", "DSTV", "MOVIE TICKET"],
    "shopping": ["AMAZON", "E-BAY", "ALIBABA", "E-COMMERCE"],
    "transport": ["UBER", "LYFT", "TAXI", "BOLT", "GOJEK"],
    "health & fitness": ["GYM", "PHARMACY", "HOSPITAL", "CLINIC"],
    "education": ["SCHOOL", "UNIVERSITY", "COLLEGE", "COURSE", "TUTORING"],
    "travel": ["FLIGHT", "HOTEL", "RENTAL CAR", "TRAVEL AGENCY"],
    "bills": ["ELECTRICITY", "WATER", "INTERNET", "GAS", "TELEPHONE"],
    "bank": ["POS", "ATM", "TRANSFER", "CHARGE"],
}


def normalize_description(description: str) -> str:
    """
    Normalize the transaction description by replacing known merchant names
    with their standardized names.
    """
    # Replace known merchants with their standardized names
    for key, value in merchant_app.items():
        if key in description.upper():
            return value

    # If no known merchant is found, return the original description
    return description


def categorize_transaction(description: str) -> str:
    """
    Categorize the transaction based on the description.
    """
    # Normalize the description
    normalized_description = normalize_description(description)

    # Check each category rule
    for category, keywords in category_rules.items():
        for keyword in keywords:
            if keyword.upper() in normalized_description.upper():
                return category

    # If no category matches, return 'other'
    return "other"
