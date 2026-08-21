import json
import os
import time

from dotenv import load_dotenv
from groq import Groq

from router import route_request


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

JUDGE_MODEL = "openai/gpt-oss-20b"
MAX_RETRIES = 2
RETRY_DELAY = 2


TEST_CASES = [
    {
        "id": 1,
        "question": "What is the capital of India?",
        "expected": "New Delhi"
    },
    {
        "id": 2,
        "question": "What is 15 multiplied by 8?",
        "expected": "120"
    },
    {
        "id": 3,
        "question": "What is the largest planet in our solar system?",
        "expected": "Jupiter"
    },
    {
        "id": 4,
        "question": "What does CPU stand for?",
        "expected": "Central Processing Unit"
    },
    {
        "id": 5,
        "question": "What is the chemical formula for water?",
        "expected": "H2O"
    },
    {
        "id": 6,
        "question": "What is a database?",
        "expected": "An organized collection of data"
    },
    {
        "id": 7,
        "question": "What is the primary purpose of an operating system?",
        "expected": "To manage computer hardware and software resources"
    },
    {
        "id": 8,
        "question": (
            "Explain the difference between supervised and "
            "unsupervised machine learning with one example of each."
        ),
        "expected": (
            "Supervised learning uses labeled data to learn a "
            "mapping between inputs and outputs. Unsupervised "
            "learning uses unlabeled data to discover patterns. "
            "Classification is supervised and clustering is unsupervised."
        )
    },
    {
        "id": 9,
        "question": (
            "What is overfitting in machine learning and what "
            "are three common ways to reduce it?"
        ),
        "expected": (
            "Overfitting occurs when a model learns training data "
            "too closely and performs poorly on unseen data. "
            "Regularization, cross-validation, early stopping, "
            "dropout and additional training data can reduce it."
        )
    },
    {
        "id": 10,
        "question": (
            "Explain the difference between precision and recall "
            "and give an example where recall is more important."
        ),
        "expected": (
            "Precision measures how many predicted positives are "
            "actually positive. Recall measures how many actual "
            "positives are identified. Recall is more important "
            "when missing a positive case is costly."
        )
    },
    {
        "id": 11,
        "question": (
            "Compare SQL and NoSQL databases and explain one "
            "situation where each would be appropriate."
        ),
        "expected": (
            "SQL databases use structured schemas and are suitable "
            "for relational data and transactions. NoSQL databases "
            "provide flexible data models and are useful for scalable "
            "or rapidly changing data."
        )
    },
    {
        "id": 12,
        "question": (
            "Explain horizontal scaling and vertical scaling "
            "and describe the main difference."
        ),
        "expected": (
            "Vertical scaling increases resources of an existing "
            "machine. Horizontal scaling adds more machines or "
            "instances."
        )
    },
    {
        "id": 13,
        "question": (
            "Design a scalable e-commerce architecture for millions "
            "of users. Explain API gateway, microservices, databases, "
            "caching, message queues, load balancing, authentication, "
            "fault tolerance and horizontal scaling."
        ),
        "expected": (
            "Use an API gateway, independently scalable services, "
            "load balancing, caching, scalable databases, asynchronous "
            "messaging, authentication, authorization, monitoring "
            "and fault tolerance."
        )
    },
    {
        "id": 14,
        "question": (
            "Design a real-time fraud detection system for a financial "
            "platform processing millions of transactions per hour."
        ),
        "expected": (
            "Use real-time event streaming, feature engineering, "
            "low-latency model serving, transaction scoring, monitoring "
            "and periodic model retraining."
        )
    },
    {
        "id": 15,
        "question": (
            "Design a globally distributed application that remains "
            "available if an entire geographic region fails."
        ),
        "expected": (
            "Use multiple geographic regions, replicated data, global "
            "load balancing, automated failover, health checks, disaster "
            "recovery and monitoring."
        )
    },
    {
        "id": 16,
        "question": (
            "Design a highly available payment processing system. "
            "Explain consistency, idempotency, retries, replication "
            "and failure recovery."
        ),
        "expected": (
            "Use strong transaction guarantees where required, "
            "idempotency keys, safe retries, database replication, "
            "failure recovery, monitoring and disaster recovery."
        )
    },
    {
        "id": 17,
        "question": (
            "Design a machine learning pipeline for predicting "
            "customer churn at a large company."
        ),
        "expected": (
            "Collect and validate data, preprocess it, engineer "
            "features, train and compare models, validate performance, "
            "deploy, monitor and retrain when necessary."
        )
    },
    {
        "id": 18,
        "question": (
            "Design a distributed system capable of processing "
            "one million events per second."
        ),
        "expected": (
            "Use partitioning, replication, distributed message "
            "queues, ordering guarantees, fault tolerance, "
            "backpressure and horizontal scaling."
        )
    },
    {
        "id": 19,
        "question": (
            "Design a recommendation system for an e-commerce "
            "platform with millions of users."
        ),
        "expected": (
            "Use candidate generation followed by ranking, user "
            "and item features, cold-start strategies, scalable "
            "model serving, offline metrics and online evaluation."
        )
    },
    {
        "id": 20,
        "question": (
            "Design a fault-tolerant microservices architecture "
            "for a large online food delivery platform."
        ),
        "expected": (
            "Use an API gateway, service discovery, independent "
            "services, suitable databases, caching, asynchronous "
            "messaging, observability, retries, circuit breakers, "
            "authentication, authorization and disaster recovery."
        )
    }
]


def judge_answer(question, expected, answer):

    prompt = f"""
Evaluate the AI answer.

Question:
{question}

Expected:
{expected}

Answer:
{answer}

Return only JSON:

{{
    "correct": true,
    "score": 1.0
}}

Score from 0.0 to 1.0.
"""

    for attempt in range(MAX_RETRIES + 1):

        try:

            response = client.chat.completions.create(
                model=JUDGE_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0,
                max_tokens=100
            )

            text = response.choices[0].message.content.strip()

            text = (
                text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            return json.loads(text)

        except Exception:

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    return {
        "correct": False,
        "score": 0
    }


def evaluate_test_set():

    results = []

    correct = 0
    low_cost_requests = 0
    high_cost_requests = 0
    escalations = 0

    actual_cost = 0.0
    baseline_cost = 0.0

    for test in TEST_CASES:

        try:

            router_result = route_request(
                test["question"]
            )

            model = router_result.get(
                "model",
                ""
            )

            if "20b" in model.lower():
                low_cost_requests += 1

            elif "120b" in model.lower():
                high_cost_requests += 1

            if router_result.get(
                "escalated",
                False
            ):
                escalations += 1

            actual_cost += float(
                router_result.get(
                    "actual_cost",
                    0
                )
            )

            baseline_cost += float(
                router_result.get(
                    "baseline_cost",
                    0
                )
            )

            answer = router_result.get(
                "answer",
                ""
            )

            judgment = judge_answer(
                test["question"],
                test["expected"],
                answer
            )

            is_correct = bool(
                judgment.get(
                    "correct",
                    False
                )
            )

            if is_correct:
                correct += 1

            results.append(
                {
                    "case": test["id"],
                    "question": test["question"],
                    "model": model,
                    "confidence": router_result.get(
                        "confidence",
                        0
                    ),
                    "complexity": router_result.get(
                        "complexity",
                        0
                    ),
                    "escalated": router_result.get(
                        "escalated",
                        False
                    ),
                    "actual_cost": router_result.get(
                        "actual_cost",
                        0
                    ),
                    "baseline_cost": router_result.get(
                        "baseline_cost",
                        0
                    ),
                    "judge_correct": is_correct,
                    "judge_score": judgment.get(
                        "score",
                        0
                    )
                }
            )

        except Exception as error:

            results.append(
                {
                    "case": test["id"],
                    "question": test["question"],
                    "model": "Error",
                    "confidence": 0,
                    "complexity": 0,
                    "escalated": False,
                    "actual_cost": 0,
                    "baseline_cost": 0,
                    "judge_correct": False,
                    "judge_score": 0,
                    "error": str(error)
                }
            )

        print(
            f"Test {test['id']} completed",
            flush=True
        )

    total = len(TEST_CASES)

    accuracy = (
        correct / total * 100
        if total
        else 0
    )

    savings = max(
        0,
        baseline_cost - actual_cost
    )

    savings_percentage = (
        savings / baseline_cost * 100
        if baseline_cost
        else 0
    )

    escalation_rate = (
        escalations / total * 100
        if total
        else 0
    )

    return {
        "accuracy": accuracy,
        "accuracy_all_cases": accuracy,
        "correct": correct,
        "total_cases": total,
        "successful_evaluations": total,
        "evaluation_errors": sum(
            1
            for item in results
            if item["model"] == "Error"
        ),
        "low_cost_requests": low_cost_requests,
        "high_cost_requests": high_cost_requests,
        "escalated_requests": escalations,
        "escalation_rate": escalation_rate,
        "actual_cost": actual_cost,
        "baseline_cost": baseline_cost,
        "savings": savings,
        "savings_percentage": savings_percentage,
        "results": results
    }


if __name__ == "__main__":
    evaluate_test_set()