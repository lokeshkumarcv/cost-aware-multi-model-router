import streamlit as st
import pandas as pd

from router import route_request
from logger import log_request, load_logs
from evaluator import evaluate_test_set


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Cost-Aware Multi-Model Router",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "AI Router"

if "result" not in st.session_state:
    st.session_state.result = None


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1250px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .project-title {
        font-size: 42px;
        font-weight: 850;
        letter-spacing: -1.8px;
        line-height: 1.1;
        margin-bottom: 12px;
    }

    .project-subtitle {
        font-size: 14px;
        line-height: 1.8;
        opacity: 0.70;
        max-width: 850px;
        margin-bottom: 38px;
    }

    .section-title {
        font-size: 23px;
        font-weight: 800;
        margin-top: 12px;
        margin-bottom: 8px;
    }

    .section-description {
        font-size: 13px;
        opacity: 0.65;
        margin-bottom: 15px;
    }

    .sidebar-heading {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1.4px;
        opacity: 0.55;
        margin-bottom: 14px;
    }

    .sidebar-model {
        font-size: 13px;
        line-height: 2.5;
        opacity: 0.75;
    }

    .sidebar-info {
        font-size: 12px;
        line-height: 1.8;
        opacity: 0.65;
    }

    textarea {
        border-radius: 12px !important;
    }

    .model-label {
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.5px;
        opacity: 0.60;
        text-transform: uppercase;
    }

    .model-name {
        font-size: 30px;
        font-weight: 850;
        margin-top: 5px;
        margin-bottom: 20px;
    }

    .footer {
        text-align: center;
        font-size: 11px;
        opacity: 0.45;
        margin-top: 30px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-heading">WORKSPACE</div>',
        unsafe_allow_html=True
    )

    if st.button(
        "⚡  AI Router",
        width="stretch"
    ):
        st.session_state.page = "AI Router"

    if st.button(
        "▦  Dashboard",
        width="stretch"
    ):
        st.session_state.page = "Dashboard"

    st.divider()

    st.markdown(
        '<div class="sidebar-heading">MODELS</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="sidebar-model">
            <span style="color:#38bdf8;">●</span>
            GPT-OSS 20B
            <br>
            <span style="color:#a78bfa;">●</span>
            GPT-OSS 120B
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="sidebar-info">
        Requests begin with the lower-cost model
        and are escalated when additional capability
        is required.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.success("Router Online")
    st.caption("Groq API")


# ============================================================
# AI ROUTER PAGE
# ============================================================

if st.session_state.page == "AI Router":

    st.markdown(
        '<div class="project-title">'
        'Cost-Aware Multi-Model Router'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="project-subtitle">'
        'Automatically routes every request to the most '
        'cost-effective model capable of handling it. '
        'Requests start with GPT-OSS 20B and are escalated '
        'to GPT-OSS 120B only when necessary.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">'
        'Your Request'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Enter your request and let the router choose the model.'
        '</div>',
        unsafe_allow_html=True
    )

    # ========================================================
    # REQUEST FORM
    # ========================================================

    with st.form(
        key="router_form",
        clear_on_submit=False,
        enter_to_submit=True
    ):

        prompt = st.text_area(
            "Request",
            placeholder="Enter your request here...",
            height=175,
            label_visibility="collapsed"
        )

        submitted = st.form_submit_button(
            "⚡  Run Request",
            type="primary",
            width="stretch"
        )

    # ========================================================
    # RUN REQUEST
    # ========================================================

    if submitted:

        if not prompt.strip():

            st.warning(
                "Please enter a request."
            )

        else:

            with st.spinner(
                "Routing your request..."
            ):

                try:

                    result = route_request(
                        prompt.strip()
                    )

                    st.session_state.result = result

                    try:

                        log_request(
                            result,
                            prompt.strip()
                        )

                    except Exception:
                        pass

                except Exception as error:

                    st.error(
                        f"Request failed: {error}"
                    )

    # ========================================================
    # RESULT
    # ========================================================

    result = st.session_state.result

    if result:

        st.divider()

        st.markdown(
            '<div class="section-title">'
            'Routing Decision'
            '</div>',
            unsafe_allow_html=True
        )

        model = str(
            result.get(
                "model",
                ""
            )
        )

        confidence = float(
            result.get(
                "confidence",
                0
            )
        )

        complexity = float(
            result.get(
                "complexity",
                0
            )
        )

        actual_cost = float(
            result.get(
                "actual_cost",
                0
            )
        )

        savings = float(
            result.get(
                "savings_percentage",
                0
            )
        )

        escalated = bool(
            result.get(
                "escalated",
                False
            )
        )

        # ====================================================
        # MODEL
        # ====================================================

        st.markdown(
            '<div class="model-label">'
            'MODEL USED'
            '</div>',
            unsafe_allow_html=True
        )

        if "120b" in model.lower():

            st.markdown(
                '<div class="model-name" '
                'style="color:#a78bfa;">'
                'GPT-OSS 120B'
                '</div>',
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                '<div class="model-name" '
                'style="color:#38bdf8;">'
                'GPT-OSS 20B'
                '</div>',
                unsafe_allow_html=True
            )

        # ====================================================
        # ROUTING METRICS
        # ====================================================

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "Confidence",
                f"{confidence:.0%}"
            )

        with c2:

            st.metric(
                "Complexity",
                f"{complexity:.2f}"
            )

        with c3:

            st.metric(
                "Request Cost",
                f"${actual_cost:.6f}"
            )

        with c4:

            st.metric(
                "Savings",
                f"{savings:.1f}%"
            )

        # ====================================================
        # ROUTING STATUS
        # ====================================================

        if escalated:

            reason = result.get(
                "escalation_reason",
                "The request required the stronger model."
            )

            st.warning(
                f"Escalated to GPT-OSS 120B\n\n"
                f"Reason: {reason}"
            )

        else:

            st.success(
                "Handled by GPT-OSS 20B"
            )

        # ====================================================
        # TOKEN USAGE
        # ========================================================

        st.markdown(
            '<div class="section-title">'
            'Token Usage'
            '</div>',
            unsafe_allow_html=True
        )

        input_tokens = int(
            result.get(
                "input_tokens",
                result.get(
                    "prompt_tokens",
                    0
                )
            ) or 0
        )

        output_tokens = int(
            result.get(
                "output_tokens",
                result.get(
                    "completion_tokens",
                    0
                )
            ) or 0
        )

        total_tokens = int(
            result.get(
                "total_tokens",
                input_tokens + output_tokens
            ) or 0
        )

        token1, token2, token3 = st.columns(3)

        with token1:

            st.metric(
                "Input Tokens",
                f"{input_tokens:,}"
            )

        with token2:

            st.metric(
                "Output Tokens",
                f"{output_tokens:,}"
            )

        with token3:

            st.metric(
                "Total Tokens",
                f"{total_tokens:,}"
            )

        # ====================================================
        # RESPONSE
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            'Response'
            '</div>',
            unsafe_allow_html=True
        )

        answer = result.get(
            "answer",
            ""
        )

        if answer:

            st.markdown(answer)

        else:

            st.warning(
                "The model returned an empty response."
            )


# ============================================================
# DASHBOARD
# ============================================================

elif st.session_state.page == "Dashboard":

    st.markdown(
        '<div class="project-title">'
        'Dashboard'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="project-subtitle">'
        'Monitor model usage, routing activity and cost efficiency.'
        '</div>',
        unsafe_allow_html=True
    )

    # ========================================================
    # LOAD LOGS
    # ========================================================

    try:

        logs = load_logs()

    except Exception:

        logs = []

    if not logs:

        st.info(
            "No requests have been recorded yet."
        )

    else:

        df = pd.DataFrame(logs)

        # ====================================================
        # NUMERIC COLUMNS
        # ====================================================

        numeric_columns = [
            "actual_cost",
            "baseline_cost",
            "savings",
            "savings_percentage",
            "confidence",
            "complexity",
            "input_tokens",
            "output_tokens",
            "total_tokens"
        ]

        for column in numeric_columns:

            if column in df.columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                ).fillna(0)

        # ====================================================
        # MODEL COUNTS
        # ====================================================

        if "model" in df.columns:

            model_names = (
                df["model"]
                .astype(str)
                .str.lower()
            )

            requests_20b = int(
                model_names
                .str.contains("20b")
                .sum()
            )

            requests_120b = int(
                model_names
                .str.contains("120b")
                .sum()
            )

        else:

            requests_20b = 0
            requests_120b = 0

        total_requests = (
            requests_20b +
            requests_120b
        )

        # ====================================================
        # COST
        # ====================================================

        if "actual_cost" in df.columns:

            router_cost = float(
                df["actual_cost"].sum()
            )

        else:

            router_cost = 0.0

        if "baseline_cost" in df.columns:

            always_120b_cost = float(
                df["baseline_cost"].sum()
            )

        else:

            always_120b_cost = 0.0

        money_saved = max(
            always_120b_cost -
            router_cost,
            0
        )

        if always_120b_cost > 0:

            savings_percentage = (
                money_saved /
                always_120b_cost *
                100
            )

        else:

            savings_percentage = 0.0

        # ====================================================
        # PERFORMANCE OVERVIEW
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            'Performance Overview'
            '</div>',
            unsafe_allow_html=True
        )

        overview1, overview2, overview3, overview4 = st.columns(4)

        with overview1:

            st.metric(
                "Total Requests",
                total_requests
            )

        with overview2:

            st.metric(
                "Router Cost",
                f"${router_cost:.5f}"
            )

        with overview3:

            st.metric(
                "Money Saved",
                f"${money_saved:.5f}"
            )

        with overview4:

            st.metric(
                "Savings",
                f"{savings_percentage:.1f}%"
            )

        # ====================================================
        # COST PERFORMANCE
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            'Cost Performance'
            '</div>',
            unsafe_allow_html=True
        )

        st.caption(
            "Cumulative router cost compared with "
            "always using GPT-OSS 120B."
        )

        cost_chart = pd.DataFrame()

        if "actual_cost" in df.columns:

            cost_chart["Router Cost"] = (
                df["actual_cost"].cumsum()
            )

        else:

            cost_chart["Router Cost"] = 0.0

        if "baseline_cost" in df.columns:

            cost_chart["Always 120B"] = (
                df["baseline_cost"].cumsum()
            )

        else:

            cost_chart["Always 120B"] = 0.0

        cost_chart.index = range(
            1,
            len(cost_chart) + 1
        )

        cost_chart.index.name = "Request"

        st.line_chart(
            cost_chart,
            y=[
                "Router Cost",
                "Always 120B"
            ],
            width="stretch",
            height=300
        )

        # ====================================================
        # MODEL USAGE
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            'Model Usage'
            '</div>',
            unsafe_allow_html=True
        )

        st.caption(
            "Requests handled by each available model."
        )

        model_chart = pd.DataFrame(
            {
                "Model": [
                    "GPT-OSS 20B",
                    "GPT-OSS 120B"
                ],
                "Requests": [
                    requests_20b,
                    requests_120b
                ]
            }
        ).set_index("Model")

        model_chart_col, _ = st.columns(
            [0.65, 0.35]
        )

        with model_chart_col:

            st.bar_chart(
                model_chart,
                y="Requests",
                width="stretch",
                height=220
            )

        # ====================================================
        # TOKEN USAGE
        # ====================================================

        if (
            "input_tokens" in df.columns
            or "output_tokens" in df.columns
            or "total_tokens" in df.columns
        ):

            st.markdown(
                '<div class="section-title">'
                'Token Usage'
                '</div>',
                unsafe_allow_html=True
            )

            st.caption(
                "Token consumption across all recorded requests."
            )

            total_input_tokens = int(
                df["input_tokens"].sum()
                if "input_tokens" in df.columns
                else 0
            )

            total_output_tokens = int(
                df["output_tokens"].sum()
                if "output_tokens" in df.columns
                else 0
            )

            total_used_tokens = int(
                df["total_tokens"].sum()
                if "total_tokens" in df.columns
                else (
                    total_input_tokens +
                    total_output_tokens
                )
            )

            token1, token2, token3 = st.columns(3)

            with token1:

                st.metric(
                    "Input Tokens",
                    f"{total_input_tokens:,}"
                )

            with token2:

                st.metric(
                    "Output Tokens",
                    f"{total_output_tokens:,}"
                )

            with token3:

                st.metric(
                    "Total Tokens",
                    f"{total_used_tokens:,}"
                )

        # ====================================================
        # RECENT REQUESTS
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            'Recent Requests'
            '</div>',
            unsafe_allow_html=True
        )

        display_columns = [
            "timestamp",
            "request",
            "model",
            "confidence",
            "complexity",
            "actual_cost",
            "savings_percentage"
        ]

        available_columns = [
            column
            for column in display_columns
            if column in df.columns
        ]

        recent = (
            df[available_columns]
            .tail(10)
            .copy()
        )

        if "request" in recent.columns:

            recent["request"] = (
                recent["request"]
                .astype(str)
                .str.slice(0, 100)
            )

        if "confidence" in recent.columns:

            recent["confidence"] = (
                recent["confidence"]
                .map(
                    lambda value:
                    f"{value:.0%}"
                )
            )

        if "complexity" in recent.columns:

            recent["complexity"] = (
                recent["complexity"]
                .map(
                    lambda value:
                    f"{value:.2f}"
                )
            )

        if "actual_cost" in recent.columns:

            recent["actual_cost"] = (
                recent["actual_cost"]
                .map(
                    lambda value:
                    f"${value:.6f}"
                )
            )

        if "savings_percentage" in recent.columns:

            recent["savings_percentage"] = (
                recent["savings_percentage"]
                .map(
                    lambda value:
                    f"{value:.1f}%"
                )
            )

        st.dataframe(
            recent.iloc[::-1],
            width="stretch",
            hide_index=True
        )

    # ========================================================
    # HELD-OUT EVALUATION
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">'
        'Held-Out Evaluation'
        '</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Evaluate the router using the predefined 20-case test set."
    )

    if st.button(
        "▶  Run 20-Case Evaluation",
        type="primary",
        width="stretch"
    ):

        with st.spinner(
            "Running evaluation..."
        ):

            try:

                evaluation = evaluate_test_set()

                st.success(
                    "Evaluation completed successfully."
                )

                # =================================================
                # EVALUATION SUMMARY
                # =================================================

                e1, e2, e3, e4 = st.columns(4)

                with e1:

                    st.metric(
                        "Accuracy",
                        f"{evaluation['accuracy']:.1f}%"
                    )

                with e2:

                    st.metric(
                        "Test Cases",
                        evaluation["total_cases"]
                    )

                with e3:

                    st.metric(
                        "Router Cost",
                        f"${evaluation['actual_cost']:.6f}"
                    )

                with e4:

                    st.metric(
                        "Savings",
                        f"{evaluation['savings_percentage']:.1f}%"
                    )

                # =================================================
                # MODEL USAGE SUMMARY
                # =================================================

                st.markdown(
                    '<div class="section-title">'
                    'Evaluation Model Usage'
                    '</div>',
                    unsafe_allow_html=True
                )

                eval1, eval2, eval3 = st.columns(3)

                with eval1:

                    st.metric(
                        "GPT-OSS 20B",
                        evaluation[
                            "low_cost_requests"
                        ]
                    )

                with eval2:

                    st.metric(
                        "GPT-OSS 120B",
                        evaluation[
                            "high_cost_requests"
                        ]
                    )

                with eval3:

                    st.metric(
                        "Escalations",
                        evaluation[
                            "escalated_requests"
                        ]
                    )

                # =================================================
                # TEST RESULTS TABLE
                # =================================================

                st.markdown(
                    '<div class="section-title">'
                    'Test Results'
                    '</div>',
                    unsafe_allow_html=True
                )

                evaluation_results = evaluation.get(
                    "results",
                    []
                )

                if evaluation_results:

                    results_df = pd.DataFrame(
                        evaluation_results
                    )

                    table_columns = [
                        "case",
                        "question",
                        "model",
                        "escalated",
                        "complexity",
                        "confidence"
                    ]

                    available_columns = [
                        column
                        for column in table_columns
                        if column in results_df.columns
                    ]

                    results_table = (
                        results_df[
                            available_columns
                        ]
                        .copy()
                    )

                    results_table = results_table.rename(
                        columns={
                            "case": "Test",
                            "question": "Question",
                            "model": "Model Used",
                            "escalated": "Escalated",
                            "complexity": "Complexity",
                            "confidence": "Confidence"
                        }
                    )

                    if "Model Used" in results_table.columns:

                        results_table["Model Used"] = (
                            results_table["Model Used"]
                            .astype(str)
                            .replace(
                                {
                                    "openai/gpt-oss-20b":
                                        "GPT-OSS 20B",
                                    "openai/gpt-oss-120b":
                                        "GPT-OSS 120B"
                                }
                            )
                        )

                    if "Escalated" in results_table.columns:

                        results_table["Escalated"] = (
                            results_table["Escalated"]
                            .map(
                                lambda value:
                                "Yes"
                                if bool(value)
                                else "No"
                            )
                        )

                    if "Complexity" in results_table.columns:

                        results_table["Complexity"] = (
                            pd.to_numeric(
                                results_table["Complexity"],
                                errors="coerce"
                            )
                            .fillna(0)
                            .map(
                                lambda value:
                                f"{value:.2f}"
                            )
                        )

                    if "Confidence" in results_table.columns:

                        results_table["Confidence"] = (
                            pd.to_numeric(
                                results_table["Confidence"],
                                errors="coerce"
                            )
                            .fillna(0)
                            .map(
                                lambda value:
                                f"{value:.0%}"
                            )
                        )

                    st.dataframe(
                        results_table,
                        width="stretch",
                        hide_index=True,
                        column_config={
                            "Test": st.column_config.NumberColumn(
                                "Test",
                                width="small"
                            ),
                            "Question": st.column_config.TextColumn(
                                "Question",
                                width="large"
                            ),
                            "Model Used": st.column_config.TextColumn(
                                "Model Used",
                                width="medium"
                            ),
                            "Escalated": st.column_config.TextColumn(
                                "Escalated",
                                width="small"
                            ),
                            "Complexity": st.column_config.TextColumn(
                                "Complexity",
                                width="small"
                            ),
                            "Confidence": st.column_config.TextColumn(
                                "Confidence",
                                width="small"
                            )
                        }
                    )

                else:

                    st.info(
                        "No test results are available."
                    )

            except Exception as error:

                st.error(
                    f"Evaluation failed: {error}"
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    '<div class="footer">'
    'Cost-Aware Multi-Model Router  •  Groq API'
    '</div>',
    unsafe_allow_html=True
)