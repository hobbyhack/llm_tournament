import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(page_title="LLM Tournament Viewer", page_icon="🏆", layout="wide")

# Main title
st.title("LLM Tournament Results Viewer")

# Sidebar navigation
view_type = st.sidebar.radio(
    "View Type", ["Single Tournament", "Multiple Tournaments Comparison"]
)

# Single Tournament View
if view_type == "Single Tournament":
    st.header("Single Tournament Results")

    # File upload
    uploaded_file = st.file_uploader("Upload tournament JSON file", type=["json"])

    if uploaded_file:
        # Load data
        tournament_data = json.load(uploaded_file)

        # Create tabs
        overview_tab, rankings_tab, details_tab = st.tabs(
            ["Overview", "Rankings", "Contender Details"]
        )

        # Tournament Overview Tab
        with overview_tab:
            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("Tournament Information")
                st.write(f"**ID:** {tournament_data['id']}")
                st.write(f"**Status:** {tournament_data['status']}")
                st.write(f"**Framework:** {tournament_data['assessment_framework_id']}")

                # Format timestamps
                start_time = datetime.fromisoformat(tournament_data["start_time"])
                end_time = datetime.fromisoformat(tournament_data["end_time"])
                duration = end_time - start_time

                st.write(f"**Start Time:** {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**End Time:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Duration:** {duration}")

            with col2:
                st.subheader("Statistics")
                stats = tournament_data["statistics"]

                st.metric("Total Contenders", stats["total_contenders"])
                st.metric("Total Matches", stats["total_matches"])
                st.metric("Completed Matches", stats["completed_matches"])

                # Progress bar
                st.write(f"**Progress:** {stats['progress_percentage']}%")
                st.progress(stats["progress_percentage"] / 100)

            # LLM config if available
            if "config" in tournament_data and "llm" in tournament_data["config"]:
                st.subheader("LLM Configuration")
                llm_config = tournament_data["config"]["llm"]

                # Display key LLM info
                st.write(f"**Provider:** {llm_config.get('provider', 'N/A')}")
                st.write(f"**Default Model:** {llm_config.get('default_model', 'N/A')}")

                # Show model mapping if available
                if "model_mapping" in llm_config:
                    st.write("**Model Mapping:**")
                    for task, model in llm_config["model_mapping"].items():
                        st.write(f"- {task}: {model}")

        # Rankings Tab
        with rankings_tab:
            st.subheader("Contender Rankings")

            # Create DataFrame from rankings
            rankings = []
            for r in tournament_data["rankings"]:
                rankings.append(
                    {
                        "Rank": r["rank"],
                        "Contender ID": r["contender_id"],
                        "Points": r["stats"]["points"],
                        "Wins": r["stats"]["wins"],
                        "Losses": r["stats"]["losses"],
                        "Draws": r["stats"]["draws"],
                        "Win %": f"{r['stats']['win_percentage'] * 100:.1f}%",
                        "Avg Score": f"{r['stats']['average_score']:.2f}",
                    }
                )

            # Display rankings table
            rankings_df = pd.DataFrame(rankings)
            st.dataframe(rankings_df, use_container_width=True)

            # Visualization
            st.subheader("Top Performers Visualization")

            # Select metric to visualize
            metric = st.selectbox(
                "Select metric to visualize:", ["Points", "Win %", "Avg Score"]
            )

            # Number of top contenders to show
            top_n = st.slider("Show top contenders:", 3, 20, 10)

            # Prepare data for visualization
            if metric == "Win %":
                # Convert percentage strings to float
                vis_df = rankings_df.copy()
                vis_df["Win %"] = vis_df["Win %"].str.rstrip("%").astype(float)
                vis_df = vis_df.sort_values(metric, ascending=False).head(top_n)
            elif metric == "Avg Score":
                # Convert avg score strings to float
                vis_df = rankings_df.copy()
                vis_df["Avg Score"] = vis_df["Avg Score"].astype(float)
                vis_df = vis_df.sort_values(metric, ascending=False).head(top_n)
            else:
                # Points is already numeric
                vis_df = rankings_df.sort_values(metric, ascending=False).head(top_n)

            # Create the visualization
            fig, ax = plt.subplots(figsize=(10, 6))

            # Create bar chart
            sns.barplot(x="Contender ID", y=metric, data=vis_df, ax=ax)

            # Formatting
            plt.xticks(rotation=45, ha="right")
            plt.title(f"Top {top_n} Contenders by {metric}")
            plt.tight_layout()

            # Display the chart
            st.pyplot(fig)

        # Contender Details Tab
        with details_tab:
            st.subheader("Contender Details")

            # Dropdown to select contender
            contender_ids = [r["contender_id"] for r in tournament_data["rankings"]]
            selected_contender = st.selectbox("Select a contender:", contender_ids)

            # Find the selected contender data
            selected_data = None
            for r in tournament_data["rankings"]:
                if r["contender_id"] == selected_contender:
                    selected_data = r
                    break

            if selected_data:
                # Contender info
                st.write(f"**Rank:** {selected_data['rank']}")

                # Content display
                st.subheader("Content")
                st.text_area("", selected_data["content"], height=150)

                # Stats display
                st.subheader("Performance Statistics")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Points", selected_data["stats"]["points"])
                    st.metric(
                        "Matches Played", selected_data["stats"]["matches_played"]
                    )

                with col2:
                    st.metric("Wins", selected_data["stats"]["wins"])
                    st.metric("Losses", selected_data["stats"]["losses"])
                    st.metric("Draws", selected_data["stats"]["draws"])

                with col3:
                    st.metric(
                        "Win %",
                        f"{selected_data['stats']['win_percentage'] * 100:.1f}%",
                    )
                    st.metric(
                        "Avg Score", f"{selected_data['stats']['average_score']:.2f}"
                    )

                # Win/Loss visualization
                st.subheader("Win/Loss Distribution")

                # Create pie chart
                fig, ax = plt.subplots(figsize=(6, 6))

                # Data
                labels = ["Wins", "Losses", "Draws"]
                values = [
                    selected_data["stats"]["wins"],
                    selected_data["stats"]["losses"],
                    selected_data["stats"]["draws"],
                ]
                colors = ["#4CAF50", "#F44336", "#FFC107"]

                # Create chart
                ax.pie(
                    values,
                    labels=labels,
                    colors=colors,
                    autopct="%1.1f%%",
                    startangle=90,
                )
                ax.axis("equal")

                # Display chart
                st.pyplot(fig)

    else:
        st.info("Upload a tournament JSON file to view results")

# Multiple Tournaments Comparison View
else:
    st.header("Multiple Tournaments Comparison")

    # File upload
    uploaded_file = st.file_uploader(
        "Upload multi-tournament comparison JSON file", type=["json"]
    )

    if uploaded_file:
        # Load data
        comparison_data = json.load(uploaded_file)

        # Display basic info
        st.subheader(f"Comparison Analysis (Timestamp: {comparison_data['timestamp']})")

        # Create DataFrame of model groups
        models_data = []

        for model, metrics in comparison_data["groups"].items():
            models_data.append(
                {
                    "Model": model,
                    "Tournaments": metrics["tournaments"],
                    "Ranking Stability": metrics["ranking_stability"],
                    "Win Rate Consistency": metrics["win_rate_consistency"],
                    "Matchup Consistency": metrics["matchup_consistency"],
                    "Score Consistency": metrics["score_consistency"],
                }
            )

        # Display model metrics table
        models_df = pd.DataFrame(models_data)
        st.dataframe(models_df.round(4), use_container_width=True)

        # Visualizations
        viz_tab1, viz_tab2 = st.tabs(["Bar Chart", "Radar Chart"])

        with viz_tab1:
            st.subheader("Metrics Comparison")

            # Reshape data for grouped bar chart
            plot_data = pd.melt(
                models_df,
                id_vars=["Model"],
                value_vars=[
                    "Ranking Stability",
                    "Win Rate Consistency",
                    "Matchup Consistency",
                    "Score Consistency",
                ],
                var_name="Metric",
                value_name="Value",
            )

            # Create grouped bar chart
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x="Metric", y="Value", hue="Model", data=plot_data, ax=ax)

            # Format chart
            plt.ylim(0, 1.05)
            plt.title("LLM Model Consistency Metrics")
            plt.xticks(rotation=15)
            plt.tight_layout()

            # Display the chart
            st.pyplot(fig)

        with viz_tab2:
            st.subheader("Radar Chart Comparison")

            # Set up categories for radar chart
            categories = [
                "Ranking Stability",
                "Win Rate Consistency",
                "Matchup Consistency",
                "Score Consistency",
            ]

            # Set up the figure
            fig = plt.figure(figsize=(8, 8))
            ax = fig.add_subplot(111, polar=True)

            # Calculate angles for each metric
            N = len(categories)
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]  # Close the loop

            # Set up the chart
            ax.set_theta_offset(np.pi / 2)
            ax.set_theta_direction(-1)
            ax.set_rlabel_position(0)

            # Add labels
            plt.xticks(angles[:-1], categories)
            ax.set_rlim(0, 1)

            # Plot each model's data
            for i, model in enumerate(models_df["Model"]):
                values = (
                    models_df.loc[models_df["Model"] == model, categories]
                    .values.flatten()
                    .tolist()
                )
                values += values[:1]  # Close the loop

                ax.plot(angles, values, linewidth=2, label=model)
                ax.fill(angles, values, alpha=0.1)

            # Add legend
            plt.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))

            # Display the chart
            st.pyplot(fig)

        # Best performing models section
        st.subheader("Best Performing Models")

        # Create table of best models
        best_data = []
        for metric, data in comparison_data["overall_comparison"].items():
            # Format metric name
            metric_name = " ".join(
                word.capitalize() for word in metric.replace("best_", "").split("_")
            )

            best_data.append(
                {
                    "Metric": metric_name,
                    "Best Model": data["group"],
                    "Value": data["value"],
                }
            )

        # Display as table
        best_df = pd.DataFrame(best_data)
        st.table(best_df.round(4))

    else:
        st.info("Upload a multi-tournament comparison JSON file to view results")

# Add footer with instructions
st.sidebar.markdown("---")
st.sidebar.subheader("About")
st.sidebar.markdown(
    """
This viewer displays results from the LLM Tournament tool, which runs round-robin tournaments 
between text candidates using LLMs as judges.

**Features:**
- View single tournament results
- Compare consistency across multiple tournaments
- Analyze contender performance
"""
)
