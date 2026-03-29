import io
import streamlit as st
import pandas as pd
from datetime import datetime
from .report_utils import (
    create_bar_chart,
    create_count_bar_chart,
    create_line_chart,
    create_scatter_plot,
    create_histogram,
    create_box_plot,
    create_pie_chart,
    generate_html_report,
)


def render_report_page():
    """Render the report generation page."""
    st.header("📝 Generate Report")

    if "current_data" not in st.session_state or st.session_state.current_data is None:
        st.warning("Please upload a dataset first!")
        if st.button("Go to Upload Page"):
            st.rerun()
        return

    df = st.session_state.current_data
    file_name = st.session_state.file_name

    if "report_items" not in st.session_state:
        st.session_state.report_items = []

    col1, col2 = st.columns([1, 3])

    with col1:
        st.subheader("Report Builder")

        add_item_type = st.selectbox(
            "Add to report",
            ["Text / Title", "Dataset Summary", "Data Preview", "Chart", "Analysis Result"],
            key="add_item_type",
        )

        # ── Text / Title ──────────────────────────────────────────────
        if add_item_type == "Text / Title":
            text_type = st.selectbox("Text type", ["Title", "Subtitle", "Paragraph"])
            text_content = st.text_area("Content")
            if st.button("Add to Report") and text_content.strip():
                st.session_state.report_items.append(
                    {"type": "text", "text_type": text_type, "content": text_content}
                )
                st.success("Added!")

        # ── Dataset Summary ───────────────────────────────────────────
        elif add_item_type == "Dataset Summary":
            if st.button("Add Dataset Summary"):
                missing_values = {}
                for col in df.columns:
                    cnt = df[col].isna().sum()
                    if cnt > 0:
                        missing_values[col] = {
                            "count": int(cnt),
                            "percentage": round(cnt / len(df) * 100, 2),
                        }

                st.session_state.report_items.append(
                    {
                        "type": "dataset_summary",
                        "content": {
                            "n_rows": len(df),
                            "n_columns": len(df.columns),
                            "column_types": {c: str(t) for c, t in df.dtypes.items()},
                            "missing_values": missing_values,
                        },
                    }
                )
                st.success("Added dataset summary!")

        # ── Data Preview ──────────────────────────────────────────────
        elif add_item_type == "Data Preview":
            preview_rows = st.slider("Rows to include", 5, 50, 10)
            if st.button("Add Data Preview"):
                st.session_state.report_items.append(
                    {"type": "data_preview", "rows": preview_rows}
                )
                st.success("Added data preview!")

        # ── Chart ─────────────────────────────────────────────────────
        elif add_item_type == "Chart":
            chart_type = st.selectbox(
                "Chart type",
                ["Bar Chart", "Count Bar Chart", "Line Chart", "Scatter Plot",
                 "Histogram", "Box Plot", "Pie Chart"],
            )

            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
            date_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
            all_cols = df.columns.tolist()

            fig = None

            if chart_type == "Bar Chart":
                if cat_cols and numeric_cols:
                    x = st.selectbox("X axis (category)", cat_cols, key="bc_x")
                    y = st.selectbox("Y axis (numeric)", numeric_cols, key="bc_y")
                    agg = st.selectbox("Aggregation", ["mean", "sum"], key="bc_agg")
                    if st.button("Preview Chart"):
                        fig = create_bar_chart(df, x, y, agg)
                else:
                    st.warning("Need at least one categorical and one numeric column.")

            elif chart_type == "Count Bar Chart":
                if cat_cols:
                    x = st.selectbox("Column", cat_cols, key="cbc_x")
                    if st.button("Preview Chart"):
                        fig = create_count_bar_chart(df, x)
                else:
                    st.warning("Need at least one categorical column.")

            elif chart_type == "Line Chart":
                if date_cols and numeric_cols:
                    x = st.selectbox("Date column", date_cols, key="lc_x")
                    y = st.selectbox("Value column", numeric_cols, key="lc_y")
                    if st.button("Preview Chart"):
                        fig = create_line_chart(df, x, y)
                else:
                    st.warning("Need a datetime column and a numeric column.")

            elif chart_type == "Scatter Plot":
                if len(numeric_cols) >= 2:
                    x = st.selectbox("X axis", numeric_cols, key="sp_x")
                    y = st.selectbox("Y axis", numeric_cols, key="sp_y")
                    color = st.selectbox("Color by (optional)", ["None"] + cat_cols, key="sp_c")
                    if st.button("Preview Chart"):
                        fig = create_scatter_plot(df, x, y, None if color == "None" else color)
                else:
                    st.warning("Need at least two numeric columns.")

            elif chart_type == "Histogram":
                if numeric_cols:
                    col = st.selectbox("Column", numeric_cols, key="hist_c")
                    bins = st.slider("Bins", 5, 100, 20, key="hist_b")
                    if st.button("Preview Chart"):
                        fig = create_histogram(df, col, bins)
                else:
                    st.warning("Need at least one numeric column.")

            elif chart_type == "Box Plot":
                if numeric_cols:
                    y = st.selectbox("Value column", numeric_cols, key="bp_y")
                    x = st.selectbox("Group by (optional)", ["None"] + cat_cols, key="bp_x")
                    if st.button("Preview Chart"):
                        fig = create_box_plot(df, y, None if x == "None" else x)
                else:
                    st.warning("Need at least one numeric column.")

            elif chart_type == "Pie Chart":
                if cat_cols:
                    cat = st.selectbox("Category column", cat_cols, key="pie_c")
                    val = st.selectbox("Value column (optional)", ["None"] + numeric_cols, key="pie_v")
                    if st.button("Preview Chart"):
                        fig = create_pie_chart(df, cat, None if val == "None" else val)
                else:
                    st.warning("Need at least one categorical column.")

            if fig is not None:
                st.plotly_chart(fig, use_container_width=True)
                if st.button("Add Chart to Report"):
                    st.session_state.report_items.append({"type": "chart", "figure": fig})
                    st.success("Chart added!")

        # ── Analysis Result ───────────────────────────────────────────
        elif add_item_type == "Analysis Result":
            history = st.session_state.get("analysis_history", [])
            if not history:
                st.info("No analyses run yet. Go to the Analyze page first.")
            else:
                labels = [f"{i+1}. {a['type']} ({a['timestamp']})" for i, a in enumerate(history)]
                selected = st.selectbox("Select analysis", labels)
                idx = labels.index(selected)
                if st.button("Add to Report"):
                    st.session_state.report_items.append(
                        {"type": "analysis_result", "analysis": history[idx]}
                    )
                    st.success("Added!")

        st.markdown("---")

        # Clear report
        if st.session_state.report_items and st.button("🗑️ Clear Report"):
            st.session_state.report_items = []
            st.rerun()

    # ── Report Preview ────────────────────────────────────────────────
    with col2:
        st.subheader("Report Preview")

        if not st.session_state.report_items:
            st.info("Add items from the left panel to build your report.")
        else:
            for item in st.session_state.report_items:
                _render_report_item(item, df)
                st.markdown("---")

            # Export
            st.subheader("Export Report")
            html = generate_html_report(st.session_state.report_items, df, file_name)
            st.download_button(
                label="⬇️ Download HTML Report",
                data=html,
                file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
            )


def _render_report_item(item: dict, df: pd.DataFrame):
    """Render a single report item in the preview pane."""
    t = item["type"]

    if t == "text":
        if item["text_type"] == "Title":
            st.title(item["content"])
        elif item["text_type"] == "Subtitle":
            st.subheader(item["content"])
        else:
            st.write(item["content"])

    elif t == "dataset_summary":
        summary = item["content"]
        st.markdown(f"**Rows:** {summary['n_rows']:,} | **Columns:** {summary['n_columns']}")
        col_df = pd.DataFrame(
            {"Column": list(summary["column_types"].keys()),
             "Type": list(summary["column_types"].values())}
        )
        st.dataframe(col_df, use_container_width=True)
        if summary["missing_values"]:
            st.markdown("**Missing Values:**")
            miss_df = pd.DataFrame(
                [{"Column": c, "Missing": v["count"], "%": v["percentage"]}
                 for c, v in summary["missing_values"].items()]
            )
            st.dataframe(miss_df, use_container_width=True)

    elif t == "data_preview":
        st.dataframe(df.head(item["rows"]), use_container_width=True)

    elif t == "chart":
        st.plotly_chart(item["figure"], use_container_width=True)

    elif t == "analysis_result":
        a = item["analysis"]
        st.markdown(f"**{a['type']}** — {a['timestamp']}")
        if a.get("columns"):
            st.markdown(f"Columns: {', '.join(a['columns'])}")
