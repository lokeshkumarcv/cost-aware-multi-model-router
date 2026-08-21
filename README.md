# Cost-Aware Multi-Model Router

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-app-red)
![Groq](https://img.shields.io/badge/API-Groq-orange)

A cost-aware AI routing system that automatically selects between two Groq-hosted language models based on request complexity and model confidence.

The system starts every request with **GPT-OSS 20B** and escalates to **GPT-OSS 120B** when the request requires additional capability.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Models](#models)
- [Routing Architecture](#routing-architecture)
- [Complexity Calculation](#complexity-calculation)
- [Confidence](#confidence)
- [Cost Tracking](#cost-tracking)
- [Token Usage](#token-usage)
- [Cost Savings](#cost-savings)
- [Project Structure](#project-structure)
- [File Descriptions](#file-descriptions)
- [Evaluation Process](#evaluation-process)
- [Streamlit Application](#streamlit-application)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Running the Evaluation](#running-the-evaluation)
- [Technologies Used](#technologies-used)
- [Key Design Principle](#key-design-principle)
- [Future Improvements](#future-improvements)

---

## Overview

Using a larger language model for every request can increase API costs unnecessarily.

This project implements a two-model routing strategy that attempts to balance **answer quality** and **API cost**.

```text
                         User Request
                              |
                              v
                    Complexity Analysis
                              |
                              v
                       GPT-OSS 20B
                              |
                    +---------+---------+
                    |                   |
             High Complexity      Low Confidence
                    |                   |
                    +---------+---------+
                              |
                         Escalate?
                         /       \
                       Yes        No
                        |          |
                        v          v
                  GPT-OSS 120B  GPT-OSS 20B
                        |          |
                        +----+-----+
                             |
                             v
                        Final Answer
                             |
                  +----------+----------+
                  |                     |
             Cost Tracking         Request Logging
                  |                     |
                  +----------+----------+
                             |
                             v
                       Streamlit UI
```

---

## Features

- Cost-aware multi-model routing
- GPT-OSS 20B first-pass model
- GPT-OSS 120B escalation model
- Request complexity calculation
- Confidence-based escalation
- Token usage tracking
- Per-request cost calculation
- Baseline cost comparison
- Cost savings calculation
- CSV-based request logging
- Streamlit web interface
- Model usage visualization
- Cost performance visualization
- Token usage dashboard
- Held-out 20-case evaluation
- Deterministic concept-based evaluation
- Terminal evaluation progress
- Evaluation analysis and routing statistics

---

## Models

The project uses two models through the Groq API.

| Model        | Role                |
|--------------|---------------------|
| GPT-OSS 20B  | First-pass model    |
| GPT-OSS 120B | Escalation model    |

Every request starts with **GPT-OSS 20B**. The request can then be escalated to **GPT-OSS 120B** when the routing conditions are met.

---

## Routing Architecture

The routing process consists of the following stages:

```text
User Request
     |
     v
Calculate Complexity
     |
     v
Call GPT-OSS 20B
     |
     v
Get Answer + Confidence
     |
     v
Check Routing Conditions
     |
     +-------------------------+
     |                         |
     v                         v
No Escalation              Escalation
     |                         |
     v                         v
20B Answer                 GPT-OSS 120B
                                |
                                v
                          Final Answer
```

The router currently uses:

| Setting               | Value |
|------------------------|-------|
| Complexity Threshold   | 0.35  |
| Confidence Threshold   | 0.82  |

A request is escalated when:

```text
complexity >= 0.35
```

or:

```text
confidence < 0.82
```

If neither condition is satisfied, the GPT-OSS 20B response is returned.

---

## Complexity Calculation

The router calculates a complexity score for each request. The score considers characteristics such as:

- Request length
- System design concepts
- Architecture
- Distributed systems
- Scalability
- Fault tolerance
- Disaster recovery
- Failover
- Replication
- Partitioning
- Message queues
- Event streaming
- Real-time processing
- Machine learning pipelines
- Multiple requirements

The resulting score is maintained between `0.0` and `1.0`.

---

## Confidence

The GPT-OSS 20B first-pass model returns an answer together with a confidence value. The response format is:

```json
{
    "answer": "model answer",
    "confidence": 0.0
}
```

The confidence value is between `0` and `1`. A confidence value below `0.82` can trigger escalation to GPT-OSS 120B.

---

## Cost Tracking

The project calculates the cost of each model request using input and output token usage.

The configured model pricing is:

| Model        | Input / 1M Tokens | Output / 1M Tokens |
|--------------|--------------------|----------------------|
| GPT-OSS 20B  | $0.075             | $0.30                |
| GPT-OSS 120B | $0.15              | $0.60                |

The cost calculation is:

```text
Input Cost  = (Input Tokens / 1,000,000) × Input Price
Output Cost = (Output Tokens / 1,000,000) × Output Price
Total Cost  = Input Cost + Output Cost
```

The router also calculates a baseline cost for comparison with the actual routing cost.

---

## Token Usage

For every request, the system tracks:

- Input tokens
- Output tokens
- Total tokens

Token usage is displayed in the Streamlit interface and stored in the request logs.

---

## Cost Savings

The system compares the actual routing cost with the baseline cost.

```text
Money Saved = Baseline Cost - Actual Cost
Savings %   = (Money Saved / Baseline Cost) × 100
```

This provides a direct measurement of the cost benefit obtained through model routing.

---

## Project Structure

```text
cost-aware-model-router/
│
├── app.py
├── router.py
├── models.py
├── cost_tracker.py
├── logger.py
├── evaluator.py
├── requirements.txt
├── .gitignore
│
└── data/
    └── requests.csv
```

---

## File Descriptions

### `app.py`

The main Streamlit application. It provides:

- AI Router interface
- User request input
- Routing result display (model info, confidence, complexity, token usage, request cost, savings, final response)
- Dashboard (cost performance chart, model usage chart, recent request history, held-out evaluation)

### `router.py`

Contains the main routing logic. Responsibilities include:

- Complexity calculation
- GPT-OSS 20B first pass
- Confidence handling
- Escalation decision
- GPT-OSS 120B escalation
- Token aggregation
- Cost calculation
- Savings calculation
- Returning the final routing result

### `models.py`

Contains the Groq client and model API functions. Responsibilities include:

- Loading the Groq API key
- Creating the Groq client
- Defining the available models
- Calling the selected model
- Returning generated responses
- Returning token usage

### `cost_tracker.py`

Handles model pricing and cost calculations. Responsibilities include:

- Model pricing
- Input token cost
- Output token cost
- Total request cost
- Baseline cost
- Savings calculation

### `logger.py`

Handles request logging. Request information is stored in `data/requests.csv`, containing:

- Timestamp
- User request
- Model used
- Confidence
- Complexity
- Escalation status
- Escalation reason
- Input tokens
- Output tokens
- Total tokens
- Actual cost
- Baseline cost
- Savings
- Savings percentage

### `evaluator.py`

Provides the held-out evaluation system. The evaluator runs a predefined set of 20 test cases. Each generated answer is evaluated using predefined concepts.

For every test:

```text
Test Score = (Matched Concepts / Total Concepts) × 100
```

The overall evaluation score is the average score across all test cases. The evaluator also reports:

- Total tests
- Average evaluation score
- Fully correct tests
- GPT-OSS 20B requests
- GPT-OSS 120B requests
- Escalations
- Escalation rate
- Router cost
- Baseline cost
- Money saved
- Savings percentage

---

## Evaluation Process

The evaluation process works as follows:

```text
Test Question
      |
      v
     Router
      |
      v
Generated Answer
      |
      v
Concept Matching
      |
      v
Test Score
```

For each test:

```text
Test Score = (Matched Concepts / Total Concepts) × 100
```

The overall evaluation score is:

```text
Overall Score = Sum of Test Scores / Number of Tests
```

The evaluation does not require an additional LLM judge call.

### Evaluation Output

When the evaluation is started, the terminal displays progress:

```text
Test 1 completed
Test 2 completed
Test 3 completed
...
Test 20 completed
```

After all tests are completed, the terminal displays an evaluation analysis:

```text
=======================================================
EVALUATION ANALYSIS
=======================================================
Total Tests       : 20
Average Score     : XX.XX%
Fully Correct     : XX
20B Requests      : XX
120B Requests     : XX
Escalations       : XX
Escalation Rate   : XX.XX%
Router Cost       : $X.XXXXXXXX
Baseline Cost     : $X.XXXXXXXX
Money Saved       : $X.XXXXXXXX
Savings           : XX.XX%
=======================================================
```

---

## Streamlit Application

The application has two main sections.

### AI Router

The AI Router allows users to:

- Enter a request
- Submit the request
- Send the request through the routing system
- View the selected model
- View confidence
- View complexity
- View token usage
- View request cost
- View savings
- View the generated response

### Dashboard

The dashboard provides:

- Total requests
- Router cost
- Money saved
- Savings percentage
- Cost performance
- Model usage
- Token usage
- Recent requests
- Held-out evaluation

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/lokeshkumarcv/cost-aware-multi-model-router.git
```

**2. Navigate to the project directory**

```bash
cd cost-aware-multi-model-router
```

**3. Create a virtual environment**

For Windows:

```bash
python -m venv venv
```

**4. Activate the virtual environment**

For Windows PowerShell:

```bash
venv\Scripts\Activate.ps1
```

**5. Install dependencies**

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root:

```text
GROQ_API_KEY=your_groq_api_key
```

The `.env` file should not be committed to GitHub. Make sure `.env` is included in `.gitignore`.

---

## Running the Application

Start the Streamlit application with:

```bash
streamlit run app.py
```

The application will normally be available at:

```text
http://localhost:8501
```

Open the displayed URL in your browser.

---

## Running the Evaluation

The evaluation can also be run directly from the terminal:

```bash
python evaluator.py
```

The terminal will show each completed test followed by the final evaluation analysis.

---

## Technologies Used

- Python
- Streamlit
- Groq API
- GPT-OSS 20B
- GPT-OSS 120B
- Pandas
- CSV
- python-dotenv
- Git
- GitHub

---

## Key Design Principle

The central idea of this project is:

> Use the lower-cost model when it is capable of handling the request, and use the higher-capability model only when additional capability is required.

The system therefore attempts to balance:

```text
          Answer Quality
                |
        +-------+-------+
        |               |
        v               v
 Model Capability     API Cost
        |               |
        +-------+-------+
                |
                v
        Cost-Aware Routing
```

Instead of sending every request directly to the larger model, the router starts with GPT-OSS 20B and escalates only when the routing conditions indicate that the request needs the larger model.

---

## Future Improvements

- Additional language models
- Dynamic routing thresholds
- More evaluation datasets
- Semantic answer evaluation
- Latency tracking
- More detailed routing analytics
- Adaptive routing
- Historical performance analysis
- Additional model providers
- Automated threshold optimization