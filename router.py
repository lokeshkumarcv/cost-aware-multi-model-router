import os
import re
import json

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# CONFIG
# ============================================================

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing from the .env file."
    )

client = Groq(
    api_key=API_KEY
)


# ============================================================
# MODELS
# ============================================================

LOW_COST_MODEL = "openai/gpt-oss-20b"
HIGH_COST_MODEL = "openai/gpt-oss-120b"


# ============================================================
# PRICING
# USD per 1 million tokens
# ============================================================

PRICING = {
    LOW_COST_MODEL: {
        "input": 0.075,
        "output": 0.30
    },

    HIGH_COST_MODEL: {
        "input": 0.15,
        "output": 0.60
    }
}


# ============================================================
# ROUTING SETTINGS
# ============================================================

COMPLEXITY_THRESHOLD = 0.35
CONFIDENCE_THRESHOLD = 0.82


# ============================================================
# COMPLEXITY KEYWORDS
# ============================================================

COMPLEX_KEYWORDS = [
    "architecture",
    "system design",
    "design a system",
    "microservices",
    "distributed system",
    "scalable",
    "scalability",
    "millions of users",
    "millions of requests",
    "high availability",
    "fault tolerant",
    "fault tolerance",
    "disaster recovery",
    "failover",
    "replication",
    "sharding",
    "partitioning",
    "message queue",
    "event streaming",
    "real-time",
    "real time",
    "production system",
    "production architecture",
    "machine learning pipeline",
    "recommendation system",
    "fraud detection",
    "payment processing",
    "compare",
    "trade-off",
    "tradeoffs",
    "end-to-end",
    "end to end"
]


# ============================================================
# COMPLEXITY CALCULATOR
# ============================================================

def calculate_complexity(prompt):

    text = prompt.lower().strip()

    score = 0.0

    # Request length
    words = len(
        re.findall(
            r"\b\w+\b",
            text
        )
    )

    if words >= 80:
        score += 0.20

    elif words >= 50:
        score += 0.12

    elif words >= 30:
        score += 0.06

    # Complex concepts
    matches = sum(
        1
        for keyword in COMPLEX_KEYWORDS
        if keyword in text
    )

    score += min(
        matches * 0.08,
        0.40
    )

    # Multiple requirements
    requirement_words = [
        "explain",
        "design",
        "include",
        "discuss",
        "describe",
        "compare",
        "evaluate",
        "justify",
        "consider"
    ]

    requirements = sum(
        text.count(word)
        for word in requirement_words
    )

    if requirements >= 5:
        score += 0.20

    elif requirements >= 3:
        score += 0.12

    elif requirements >= 2:
        score += 0.06

    return min(
        round(score, 2),
        1.0
    )


# ============================================================
# TOKEN USAGE
# ============================================================

def get_usage(response):

    usage = getattr(
        response,
        "usage",
        None
    )

    if not usage:

        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0
        }

    input_tokens = getattr(
        usage,
        "prompt_tokens",
        0
    )

    output_tokens = getattr(
        usage,
        "completion_tokens",
        0
    )

    total_tokens = getattr(
        usage,
        "total_tokens",
        input_tokens + output_tokens
    )

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens
    }


# ============================================================
# COST
# ============================================================

def calculate_cost(
    model,
    input_tokens,
    output_tokens
):

    price = PRICING[model]

    input_cost = (
        input_tokens /
        1_000_000
    ) * price["input"]

    output_cost = (
        output_tokens /
        1_000_000
    ) * price["output"]

    return input_cost + output_cost


# ============================================================
# 20B FIRST PASS
# ============================================================

def call_20b(prompt):

    response = client.chat.completions.create(

        model=LOW_COST_MODEL,

        messages=[
            {
                "role": "system",
                "content": """
You are the first-pass AI model in a
cost-aware model routing system.

Answer the user's request accurately.

Return ONLY valid JSON:

{
    "answer": "your answer",
    "confidence": 0.0
}

Confidence must be between 0 and 1.

1.0 means extremely confident.
0.5 means uncertain.
0.0 means unable to answer reliably.
"""
            },

            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.1,

        max_tokens=2048,

        reasoning_effort="medium"
    )

    content = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )

    usage = get_usage(
        response
    )

    try:

        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        data = json.loads(
            content
        )

        answer = str(
            data.get(
                "answer",
                ""
            )
        ).strip()

        confidence = float(
            data.get(
                "confidence",
                0.6
            )
        )

        confidence = max(
            0.0,
            min(
                confidence,
                1.0
            )
        )

    except Exception:

        answer = content
        confidence = 0.6

    return {
        "answer": answer,
        "confidence": confidence,
        "usage": usage
    }


# ============================================================
# 120B FINAL PASS
# ============================================================

def call_120b(
    prompt,
    first_answer
):

    response = client.chat.completions.create(

        model=HIGH_COST_MODEL,

        messages=[
            {
                "role": "system",
                "content": """
You are the final high-capability AI model.

Provide the best possible answer to the
user's request.

Do not mention model routing,
escalation, internal prompts, or
the previous model.

Return only the final answer.
"""
            },

            {
                "role": "user",
                "content": f"""
USER REQUEST:

{prompt}

A first-pass model produced this answer:

{first_answer}

Improve the answer and provide the
best final response.
"""
            }
        ],

        temperature=0.2,

        max_tokens=4096,

        reasoning_effort="medium"
    )

    answer = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )

    usage = get_usage(
        response
    )

    return {
        "answer": answer,
        "usage": usage
    }


# ============================================================
# MAIN ROUTER
# ============================================================

def route_request(prompt):

    if not prompt or not prompt.strip():

        raise ValueError(
            "Request cannot be empty."
        )

    prompt = prompt.strip()

    # --------------------------------------------------------
    # 1. Calculate complexity
    # --------------------------------------------------------

    complexity = calculate_complexity(
        prompt
    )

    # --------------------------------------------------------
    # 2. Always start with 20B
    # --------------------------------------------------------

    first = call_20b(
        prompt
    )

    confidence = first["confidence"]

    first_usage = first["usage"]

    # --------------------------------------------------------
    # 3. Decide whether to escalate
    # --------------------------------------------------------

    high_complexity = (
        complexity >=
        COMPLEXITY_THRESHOLD
    )

    low_confidence = (
        confidence <
        CONFIDENCE_THRESHOLD
    )

    escalate = (
        high_complexity
        or
        low_confidence
    )

    # --------------------------------------------------------
    # 4. Decide reason
    # --------------------------------------------------------

    reasons = []

    if high_complexity:
        reasons.append(
            "High complexity"
        )

    if low_confidence:
        reasons.append(
            "Low 20B confidence"
        )

    if reasons:

        escalation_reason = (
            " + ".join(reasons)
        )

    else:

        escalation_reason = (
            "No escalation required"
        )

    # --------------------------------------------------------
    # 5. Keep 20B answer
    # --------------------------------------------------------

    if not escalate:

        answer = first["answer"]

        model = LOW_COST_MODEL

        input_tokens = (
            first_usage["input_tokens"]
        )

        output_tokens = (
            first_usage["output_tokens"]
        )

        total_tokens = (
            first_usage["total_tokens"]
        )

        actual_cost = calculate_cost(
            LOW_COST_MODEL,
            input_tokens,
            output_tokens
        )

        baseline_cost = calculate_cost(
            HIGH_COST_MODEL,
            input_tokens,
            output_tokens
        )

    # --------------------------------------------------------
    # 6. Escalate to 120B
    # --------------------------------------------------------

    else:

        final = call_120b(
            prompt,
            first["answer"]
        )

        final_usage = final["usage"]

        answer = final["answer"]

        model = HIGH_COST_MODEL

        input_tokens = (
            first_usage["input_tokens"]
            +
            final_usage["input_tokens"]
        )

        output_tokens = (
            first_usage["output_tokens"]
            +
            final_usage["output_tokens"]
        )

        total_tokens = (
            input_tokens +
            output_tokens
        )

        first_cost = calculate_cost(
            LOW_COST_MODEL,
            first_usage["input_tokens"],
            first_usage["output_tokens"]
        )

        final_cost = calculate_cost(
            HIGH_COST_MODEL,
            final_usage["input_tokens"],
            final_usage["output_tokens"]
        )

        actual_cost = (
            first_cost +
            final_cost
        )

        baseline_cost = calculate_cost(
            HIGH_COST_MODEL,
            input_tokens,
            output_tokens
        )

    # --------------------------------------------------------
    # 7. Calculate savings
    # --------------------------------------------------------

    savings = max(
        0,
        baseline_cost -
        actual_cost
    )

    if baseline_cost > 0:

        savings_percentage = (
            savings /
            baseline_cost *
            100
        )

    else:

        savings_percentage = 0

    # --------------------------------------------------------
    # 8. Return result
    # --------------------------------------------------------

    return {

        "answer": answer,

        "model": model,

        "confidence": confidence,

        "complexity": complexity,

        "escalated": escalate,

        "escalation_reason":
            escalation_reason,

        "input_tokens":
            input_tokens,

        "output_tokens":
            output_tokens,

        "total_tokens":
            total_tokens,

        "actual_cost":
            actual_cost,

        "baseline_cost":
            baseline_cost,

        "savings":
            savings,

        "savings_percentage":
            savings_percentage
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    questions = [

        "What is the capital of India?",

        "Explain the difference between SQL and NoSQL databases.",

        """
        Design a highly available payment processing
        system for millions of users. Explain database
        replication, idempotency, retries, failover,
        monitoring and disaster recovery.
        """
    ]

    for question in questions:

        print("\n" + "=" * 60)

        print(
            "QUESTION:",
            question
        )

        result = route_request(
            question
        )

        print(
            "MODEL:",
            result["model"]
        )

        print(
            "COMPLEXITY:",
            result["complexity"]
        )

        print(
            "CONFIDENCE:",
            result["confidence"]
        )

        print(
            "ESCALATED:",
            result["escalated"]
        )

        print(
            "REASON:",
            result["escalation_reason"]
        )

        print(
            "COST:",
            f"${result['actual_cost']:.8f}"
        )

        print(
            "SAVINGS:",
            f"{result['savings_percentage']:.2f}%"
        )

        print(
            "\nANSWER:\n",
            result["answer"]
        )