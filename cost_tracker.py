LOW_COST_INPUT = 0.075
LOW_COST_OUTPUT = 0.30

HIGH_COST_INPUT = 0.15
HIGH_COST_OUTPUT = 0.60


def calculate_cost(model, input_tokens, output_tokens):
    if model == "openai/gpt-oss-20b":
        input_price = LOW_COST_INPUT
        output_price = LOW_COST_OUTPUT

    elif model == "openai/gpt-oss-120b":
        input_price = HIGH_COST_INPUT
        output_price = HIGH_COST_OUTPUT

    else:
        raise ValueError(f"Unknown model: {model}")

    input_cost = (input_tokens / 1_000_000) * input_price
    output_cost = (output_tokens / 1_000_000) * output_price

    return input_cost + output_cost


def calculate_baseline_cost(input_tokens, output_tokens):
    return calculate_cost(
        "openai/gpt-oss-120b",
        input_tokens,
        output_tokens
    )


def calculate_savings(actual_cost, baseline_cost):
    savings = baseline_cost - actual_cost

    if baseline_cost == 0:
        savings_percentage = 0

    else:
        savings_percentage = (
            savings / baseline_cost
        ) * 100

    return {
        "savings": max(savings, 0),
        "savings_percentage": max(savings_percentage, 0)
    }