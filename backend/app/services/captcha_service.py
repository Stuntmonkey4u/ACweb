import random

CAPTCHA_EXPIRY_SECONDS: int = 300  # 5 minutes

def generate_math_challenge() -> tuple[str, str]:
    """
    Generates a simple math problem (e.g., "What is 2 + 3?") and its answer.
    Operators are + or *. Numbers are between 1 and 10.
    """
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operator = random.choice(["+", "*"])

    if operator == "+":
        question = f"What is {num1} + {num2}?"
        answer = str(num1 + num2)
    elif operator == "*":
        question = f"What is {num1} * {num2}?"
        answer = str(num1 * num2)
    else:
        # Should not happen with current random.choice
        raise ValueError("Invalid operator selected")

    return question, answer
