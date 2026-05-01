import os
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

DATA_URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
LOCAL_DATA_FILE = "spacex_launch_dash.csv"

# Load dataset from local file first, then fall back to IBM-hosted CSV
if os.path.exists(LOCAL_DATA_FILE):
    spacex_df = pd.read_csv(LOCAL_DATA_FILE)
else:
    spacex_df = pd.read_csv(DATA_URL)

# Clean/standardize key columns
required_columns = ["Launch Site", "class", "Payload Mass (kg)", "Booster Version Category"]
missing = [col for col in required_columns if col not in spacex_df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}. Found columns: {list(spacex_df.columns)}")

spacex_df["Launch Site"] = spacex_df["Launch Site"].astype(str)
spacex_df["Booster Version Category"] = spacex_df["Booster Version Category"].astype(str)
spacex_df["class"] = pd.to_numeric(spacex_df["class"], errors="coerce").fillna(0).astype(int)
spacex_df["Payload Mass (kg)"] = pd.to_numeric(spacex_df["Payload Mass (kg)"], errors="coerce")
spacex_df = spacex_df.dropna(subset=["Payload Mass (kg)"]).copy()

min_payload = int(spacex_df["Payload Mass (kg)"].min())
max_payload = int(spacex_df["Payload Mass (kg)"].max())

site_options = [{"label": "All Sites", "value": "ALL"}] + [
    {"label": site, "value": site} for site in sorted(spacex_df["Launch Site"].unique())
]

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={
                "textAlign": "center",
                "color": "#503D36",
                "fontSize": 40,
                "marginTop": "35px",
                "marginBottom": "25px",
            },
        ),

        html.Div(
            children=[
                html.Label("Select Launch Site:", style={"fontWeight": "bold"}),
                dcc.Dropdown(
                    id="site-dropdown",
                    options=site_options,
                    value="ALL",
                    placeholder="Select a Launch Site here",
                    searchable=True,
                    clearable=False,
                    style={"width": "100%"},
                ),
            ],
            style={"width": "85%", "margin": "0 auto 35px auto"},
        ),

        html.Div(
            dcc.Graph(id="success-pie-chart"),
            style={"width": "85%", "margin": "0 auto"},
        ),

        html.Div(
            children=[
                html.Label("Select Payload Range (kg):", style={"fontWeight": "bold"}),
                dcc.RangeSlider(
                    id="payload-slider",
                    min=0,
                    max=10000,
                    step=1000,
                    marks={i: str(i) for i in range(0, 10001, 2500)},
                    value=[min_payload, max_payload],
                    tooltip={"placement": "bottom", "always_visible": True},
                ),
            ],
            style={"width": "85%", "margin": "35px auto 20px auto"},
        ),

        html.Div(
            dcc.Graph(id="success-payload-scatter-chart"),
            style={"width": "85%", "margin": "0 auto 50px auto"},
        ),
    ]
)


@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def update_pie_chart(selected_site):
    if selected_site == "ALL":
        success_by_site = (
            spacex_df[spacex_df["class"] == 1]
            .groupby("Launch Site", as_index=False)
            .size()
            .rename(columns={"size": "Success Count"})
        )

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=success_by_site["Launch Site"],
                    values=success_by_site["Success Count"],
                    hole=0,
                    textinfo="percent",
                    hovertemplate="%{label}<br>Successful launches: %{value}<extra></extra>",
                )
            ]
        )
        fig.update_layout(title="Total Successful Launches by Site")
        return fig

    filtered_df = spacex_df[spacex_df["Launch Site"] == selected_site].copy()
    outcome_counts = (
        filtered_df["class"]
        .value_counts()
        .reindex([0, 1], fill_value=0)
        .reset_index()
    )
    outcome_counts.columns = ["class", "count"]
    outcome_counts["Outcome"] = outcome_counts["class"].map({0: "Failure", 1: "Success"})

    fig = go.Figure(
        data=[
            go.Pie(
                labels=outcome_counts["Outcome"],
                values=outcome_counts["count"],
                hole=0,
                textinfo="percent+label",
                hovertemplate="%{label}: %{value}<extra></extra>",
            )
        ]
    )
    fig.update_layout(title=f"Launch Outcome Success Rate for {selected_site}")
    return fig


@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range

    filtered_df = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= low)
        & (spacex_df["Payload Mass (kg)"] <= high)
    ].copy()

    if selected_site != "ALL":
        filtered_df = filtered_df[filtered_df["Launch Site"] == selected_site].copy()

    fig = go.Figure()

    if filtered_df.empty:
        fig.update_layout(
            title="Payload Mass vs. Launch Outcome",
            xaxis_title="Payload Mass (kg)",
            yaxis_title="Launch Outcome",
            annotations=[
                {
                    "text": "No launches in the selected payload range.",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 16},
                }
            ],
        )
        return fig

    # Manual traces avoid Plotly Express category-order bugs on newer Python/Pandas versions.
    for booster, group in filtered_df.groupby("Booster Version Category", sort=True):
        fig.add_trace(
            go.Scatter(
                x=group["Payload Mass (kg)"],
                y=group["class"],
                mode="markers",
                name=str(booster),
                text=group["Launch Site"],
                customdata=group[["Booster Version Category"]],
                hovertemplate=(
                    "Launch Site: %{text}<br>"
                    "Payload Mass (kg): %{x}<br>"
                    "Launch Outcome: %{y}<br>"
                    "Booster: %{customdata[0]}<extra></extra>"
                ),
                marker={"size": 10, "opacity": 0.75},
            )
        )

    title_site = "All Sites" if selected_site == "ALL" else selected_site
    fig.update_layout(
        title=f"Payload Mass vs. Launch Outcome for {title_site}",
        xaxis_title="Payload Mass (kg)",
        yaxis_title="Launch Outcome",
        legend_title="Booster Version Category",
        yaxis={
            "tickmode": "array",
            "tickvals": [0, 1],
            "ticktext": ["Failure", "Success"],
        },
        template="plotly_white",
    )

    return fig


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
