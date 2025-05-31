import pytest
from backend.app.services import captcha_service

def test_generate_math_challenge_returns_strings():
    question, answer = captcha_service.generate_math_challenge()
    assert isinstance(question, str)
    assert isinstance(answer, str)
    assert "What is" in question # Check for expected question format

def test_generate_math_challenge_answer_is_correct():
    for _ in range(20): # Run multiple times to test different challenges
        question, answer_str = captcha_service.generate_math_challenge()

        # Parse the question
        parts = question.replace("What is ", "").replace("?", "").split()
        num1 = int(parts[0])
        operator = parts[1]
        num2 = int(parts[2])

        expected_answer = -1
        if operator == "+":
            expected_answer = num1 + num2
        elif operator == "*":
            expected_answer = num1 * num2

        assert str(expected_answer) == answer_str, f"Question: {question}, Expected: {expected_answer}, Got: {answer_str}"

def test_generate_math_challenge_randomness():
    results = set()
    for _ in range(50): # Generate a few challenges
        question, _ = captcha_service.generate_math_challenge()
        results.add(question)

    # Expect more than 1 unique question if randomness is working.
    # With small number ranges (1-10) and 2 ops, duplicates are possible, but with 50 attempts,
    # we should see a good variety.
    # Max unique questions = 10 * 10 (for +) + 10 * 10 (for *) = 200 (if order matters, e.g. 2+3 vs 3+2)
    # Or 55 + 55 = 110 if order doesn't matter for unique questions (e.g. 2+3 is same as 3+2).
    # The question string "What is X + Y?" makes order matter.
    # For numbers 1-10, there are 100 pairs for '+' and 100 for '*'.
    # Some results might be the same (e.g. 2*3=6, 3*2=6).
    # But question strings "What is 2 * 3?" and "What is 3 * 2?" are different.
    assert len(results) > 10, "Expected a variety of questions, got too few unique ones."

    # Check if both operators appear
    plus_found = False
    multiply_found = False
    for q_text in results:
        if "+" in q_text:
            plus_found = True
        if "*" in q_text:
            multiply_found = True

    assert plus_found and multiply_found, "Both '+' and '*' operators should appear in generated questions over several runs."

def test_captcha_expiry_constant():
    assert captcha_service.CAPTCHA_EXPIRY_SECONDS == 300 # 5 minutes
    assert isinstance(captcha_service.CAPTCHA_EXPIRY_SECONDS, int)
