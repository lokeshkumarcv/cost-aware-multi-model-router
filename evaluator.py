import re
from router import route_request


TEST_CASES = [
    {
        "id": 1,
        "question": "What is the capital of India?",
        "concepts": ["new delhi"]
    },
    {
        "id": 2,
        "question": "What is 15 multiplied by 8?",
        "concepts": ["120"]
    },
    {
        "id": 3,
        "question": "What is the largest planet in our solar system?",
        "concepts": ["jupiter"]
    },
    {
        "id": 4,
        "question": "What does CPU stand for?",
        "concepts": ["central processing unit"]
    },
    {
        "id": 5,
        "question": "What is the chemical formula for water?",
        "concepts": ["h2o"]
    },
    {
        "id": 6,
        "question": "What is a database?",
        "concepts": [
            "organized collection",
            "data"
        ]
    },
    {
        "id": 7,
        "question": "What is the primary purpose of an operating system?",
        "concepts": [
            "manage hardware",
            "manage software",
            "resources"
        ]
    },
    {
        "id": 8,
        "question": (
            "What is the difference between supervised and "
            "unsupervised machine learning?"
        ),
        "concepts": [
            "labeled data",
            "unlabeled data",
            "supervised learning",
            "unsupervised learning"
        ]
    },
    {
        "id": 9,
        "question": (
            "What is overfitting in machine learning and "
            "how can it be reduced?"
        ),
        "concepts": [
            "training data",
            "unseen data",
            "regularization",
            "cross validation"
        ]
    },
    {
        "id": 10,
        "question": (
            "Explain the difference between precision and recall "
            "and give a situation where recall is more important."
        ),
        "concepts": [
            "precision",
            "recall",
            "positive predictions",
            "actual positives",
            "missing a positive"
        ]
    },
    {
        "id": 11,
        "question": (
            "Compare SQL and NoSQL databases and explain when "
            "each would be appropriate."
        ),
        "concepts": [
            "relational",
            "structured",
            "flexible schema",
            "scalable"
        ]
    },
    {
        "id": 12,
        "question": (
            "Explain horizontal scaling and vertical scaling "
            "and describe their main difference."
        ),
        "concepts": [
            "vertical scaling",
            "horizontal scaling",
            "increase resources",
            "multiple machines"
        ]
    },
    {
        "id": 13,
        "question": (
            "Explain how caching can improve the performance "
            "of a web application."
        ),
        "concepts": [
            "cache",
            "frequently accessed",
            "faster response",
            "reduce database requests"
        ]
    },
    {
        "id": 14,
        "question": (
            "Explain the role of a load balancer in a distributed "
            "application."
        ),
        "concepts": [
            "distribute traffic",
            "multiple servers",
            "availability",
            "scalability"
        ]
    },
    {
        "id": 15,
        "question": (
            "Design a scalable e-commerce architecture for millions "
            "of users. Explain the major components required."
        ),
        "concepts": [
            "api gateway",
            "load balancing",
            "caching",
            "database",
            "message queue",
            "authentication",
            "monitoring"
        ]
    },
    {
        "id": 16,
        "question": (
            "Design a real-time fraud detection system for a financial "
            "platform processing millions of transactions per hour."
        ),
        "concepts": [
            "event streaming",
            "feature processing",
            "machine learning model",
            "real time",
            "transaction scoring",
            "monitoring",
            "model retraining"
        ]
    },
    {
        "id": 17,
        "question": (
            "Design a globally distributed application that remains "
            "available if an entire geographic region fails."
        ),
        "concepts": [
            "multiple regions",
            "replicated data",
            "global load balancing",
            "failover",
            "health checks",
            "disaster recovery",
            "monitoring"
        ]
    },
    {
        "id": 18,
        "question": (
            "Design a highly available payment processing system. "
            "Explain consistency, idempotency, retries, replication, "
            "and failure recovery."
        ),
        "concepts": [
            "consistency",
            "idempotency",
            "retries",
            "database replication",
            "failure recovery",
            "monitoring"
        ]
    },
    {
        "id": 19,
        "question": (
            "Design a distributed system capable of processing "
            "one million events per second."
        ),
        "concepts": [
            "partitioning",
            "replication",
            "message queue",
            "fault tolerance",
            "backpressure",
            "horizontal scaling"
        ]
    },
    {
        "id": 20,
        "question": (
            "Design a fault-tolerant microservices architecture for "
            "a large online food delivery platform."
        ),
        "concepts": [
            "api gateway",
            "service discovery",
            "microservices",
            "database",
            "caching",
            "message queue",
            "monitoring",
            "fault tolerance"
        ]
    }
]


def normalize_text(text):
    text = str(text).lower()

    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def concept_found(answer, concept):
    answer = normalize_text(answer)
    concept = normalize_text(concept)

    if concept in answer:
        return True

    words = concept.split()

    if len(words) == 1:
        return False

    return all(
        word in answer
        for word in words
    )


def calculate_score(answer, concepts):
    if not concepts:
        return 0.0, 0, 0

    matched = sum(
        concept_found(answer, concept)
        for concept in concepts
    )

    total = len(concepts)

    score = (
        matched / total
    ) * 100

    return score, matched, total


def print_analysis(
    results,
    low_cost_requests,
    high_cost_requests,
    escalations,
    actual_cost,
    baseline_cost
):

    total_tests = len(results)

    total_score = sum(
        result["score"]
        for result in results
    )

    average_score = (
        total_score / total_tests
        if total_tests
        else 0
    )

    fully_correct = sum(
        result["score"] == 100
        for result in results
    )

    savings = max(
        baseline_cost - actual_cost,
        0
    )

    savings_percentage = (
        savings / baseline_cost * 100
        if baseline_cost
        else 0
    )

    escalation_rate = (
        escalations / total_tests * 100
        if total_tests
        else 0
    )

    print()
    print("=" * 55)
    print("EVALUATION ANALYSIS")
    print("=" * 55)

    print(
        f"Total Tests       : {total_tests}"
    )

    print(
        f"Average Score     : {average_score:.2f}%"
    )

    print(
        f"Fully Correct     : {fully_correct}"
    )

    print(
        f"20B Requests      : {low_cost_requests}"
    )

    print(
        f"120B Requests     : {high_cost_requests}"
    )

    print(
        f"Escalations       : {escalations}"
    )

    print(
        f"Escalation Rate   : {escalation_rate:.2f}%"
    )

    print(
        f"Router Cost       : ${actual_cost:.8f}"
    )

    print(
        f"Baseline Cost     : ${baseline_cost:.8f}"
    )

    print(
        f"Money Saved       : ${savings:.8f}"
    )

    print(
        f"Savings           : {savings_percentage:.2f}%"
    )

    print("=" * 55)
    print()


def evaluate_test_set():

    results = []

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

            model = str(
                router_result.get(
                    "model",
                    ""
                )
            )

            model_name = model.lower()

            if "120b" in model_name:

                high_cost_requests += 1

            elif "20b" in model_name:

                low_cost_requests += 1

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

            score, matched, total = calculate_score(
                answer,
                test["concepts"]
            )

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
                    "score": score,
                    "matched_concepts": matched,
                    "total_concepts": total,
                    "actual_cost": router_result.get(
                        "actual_cost",
                        0
                    ),
                    "baseline_cost": router_result.get(
                        "baseline_cost",
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
                    "score": 0,
                    "matched_concepts": 0,
                    "total_concepts": len(
                        test["concepts"]
                    ),
                    "actual_cost": 0,
                    "baseline_cost": 0,
                    "error": str(error)
                }
            )

        print(
            f"Test {test['id']} completed",
            flush=True
        )

    print_analysis(
        results=results,
        low_cost_requests=low_cost_requests,
        high_cost_requests=high_cost_requests,
        escalations=escalations,
        actual_cost=actual_cost,
        baseline_cost=baseline_cost
    )

    total_tests = len(results)

    average_score = (
        sum(
            result["score"]
            for result in results
        ) / total_tests
        if total_tests
        else 0
    )

    fully_correct = sum(
        result["score"] == 100
        for result in results
    )

    savings = max(
        baseline_cost - actual_cost,
        0
    )

    savings_percentage = (
        savings / baseline_cost * 100
        if baseline_cost
        else 0
    )

    escalation_rate = (
        escalations / total_tests * 100
        if total_tests
        else 0
    )

    return {
        "accuracy": average_score,
        "average_score": average_score,
        "correct": fully_correct,
        "total_cases": total_tests,
        "successful_evaluations": total_tests,
        "evaluation_errors": 0,
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