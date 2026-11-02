# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
    id="site-dropdown",
    options=[
        {"label": "All Sites", "value": "ALL"}
    ] + [
        {"label": site, "value": site}
        for site in spacex_df["Launch Site"].unique()
    ],
    value="ALL",
    placeholder="Select a Launch Site",
    searchable=True,
    clearable=False
),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                               dcc.RangeSlider(
    id="payload-slider",
    min=0,
    max=10000,
    step=1000,
    marks={
        0: "0",
        2500: "2500",
        5000: "5000",
        7500: "7500",
        10000: "10000"
    },
    value=[min_payload, max_payload]
),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value")
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        successes = (
            spacex_df.groupby("Launch Site", as_index=False)["class"]
            .sum()
        )

        fig = px.pie(
            successes,
            names="Launch Site",
            values="class",
            title="Successful Launches by Site"
        )

    else:
        filtered_df = spacex_df[
            spacex_df["Launch Site"] == entered_site
        ]

        counts = (
            filtered_df["class"]
            .value_counts()
            .rename_axis("class")
            .reset_index(name="Count")
        )

        counts["Outcome"] = counts["class"].map({
            0: "Unsuccessful",
            1: "Successful"
        })

        fig = px.pie(
            counts,
            names="Outcome",
            values="Count",
            title=f"Launch Outcomes — {entered_site}"
        )

    return fig
        # return the outcomes piechart for a selected site

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    Input("site-dropdown", "value"),
    Input("payload-slider", "value")
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range

    filtered_df = spacex_df[
        spacex_df["Payload Mass (kg)"].between(low, high)
    ]

    if entered_site != "ALL":
        filtered_df = filtered_df[
            filtered_df["Launch Site"] == entered_site
        ]

    site_title = (
        "All Sites" if entered_site == "ALL" else entered_site
    )

    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        hover_data=["Launch Site"],
        title=f"Payload Mass and Launch Outcome — {site_title}",
        labels={
            "Payload Mass (kg)": "Payload Mass (kg)",
            "class": "Outcome",
            "Booster Version Category": "Booster Version"
        }
    )

    fig.update_yaxes(
        tickmode="array",
        tickvals=[0, 1],
        ticktext=["Unsuccessful", "Successful"],
        range=[-0.1, 1.1]
    )

    return fig
# Run the app
if __name__ == '__main__':
    app.run()

