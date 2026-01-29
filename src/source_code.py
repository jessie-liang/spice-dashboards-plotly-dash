# load python libraries
from dash import dcc, html, Dash, dash_table, ctx, no_update
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import numpy as np
from dash_bootstrap_templates import load_figure_template
import dash_bootstrap_components as dbc
import country_converter as coco
import logging
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

# read raw data
data = pd.read_csv("data/data_raw.csv")
# read reference table
ref_table = pd.read_csv("data/country_code_conversion.csv")

# clean relevant numeric columns in `data` and `ref_table`
data["Area Code (M49)"] = (
    data["Area Code (M49)"]
    .astype(str)
    .str.replace('"', "", regex=False)
    .str.strip()
    .astype("Int64")
)
ref_table["Numeric code"] = (
    ref_table["Numeric code"]
    .astype(str)
    .str.replace('"', "", regex=False)
    .str.strip()
    .astype("Int64")
)
ref_table["Alpha-3 code"] = (
    ref_table["Alpha-3 code"].astype(str).str.replace('"', "", regex=False).str.strip()
)
data["Year"] = data["Year"].astype(int)

# fix inconsistency between raw data and reference table
data.loc[data["Area"] == "Sudan", "Area Code (M49)"] = 736

# shorten a long area name
data["Area"] = data["Area"].replace(
    "United Kingdom of Great Britain and Northern Ireland", "UK and Northern Ireland"
)

# left join `data` and `ref_table` using each area's M49 code
# so that latitude and longitude information can be included in `data`
data = data.merge(
    ref_table, how="left", left_on="Area Code (M49)", right_on="Numeric code"
)

# use coco library to tell which continent each area is located in
cc = coco.CountryConverter()
logging.getLogger("country_converter").setLevel(logging.ERROR)
data["Continent"] = cc.convert(
    names=data["Area Code (M49)"], to="continent", src="UNnumeric"
)
data["Continent"] = data["Continent"].replace("not found", pd.NA)

# filter out those area which cannot be matched with a continent
data = data[data["Continent"].notna()]
# select only relevant columns in `data`
data = data[
    [
        "Area",
        "Continent",  #'Latitude (average)', 'Longitude (average)',
        "Alpha-3 code",
        "Year",
        "Import",
        "Export ",
        "Production",
        "Consumption",
        "Unit",
    ]
]

# rename dirty column names
data = data.rename(columns={"Export ": "Export", "Alpha-3 code": "ISO-3"})

# use grouping to eliminate duplicate rows
data = (
    data.groupby(["Area", "Continent", "ISO-3", "Year"])
    .agg({"Import": "sum", "Export": "sum", "Production": "sum", "Consumption": "sum"})
    .reset_index()
)

# calculate two derived columns: `Net Trade` and `Self-Sufficiency Ratio`
data["Net Trade"] = data["Export"] - data["Import"]
data["Self-Sufficiency Ratio"] = data["Production"] / data["Consumption"]

# load dashboard theme
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
load_figure_template("CERULEAN")

# create an app object
app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN, dbc_css])

# tab 4 report card style
card_style = {
    "height": "70px",
    "alignItems": "center",
    "justifyContent": "center",
    "textAlign": "center",
}

# design the app layout
app.layout = dbc.Container(
    [
        dcc.Tabs(
            id="tabs",
            children=[
                # Tab 1: Global Overview
                dcc.Tab(
                    label="Global Overview",
                    value="tab1",
                    children=[
                        # Title of Tab 1
                        dbc.Row(
                            html.H1(id="global-title", style={"text-align": "center"})
                        ),
                        # Description of Tab 1
                        dbc.Row(
                            dbc.Col(
                                dbc.Card(
                                    [dbc.Row(html.P(id="description"))],
                                    className="mb-3",
                                ),
                                width=9,
                            ),
                            justify="center",
                        ),
                        # Contents of Tab 1
                        dbc.Row(
                            [
                                # Leftmost column: interactive elements (two drop down menus)
                                dbc.Col(
                                    [
                                        # Drop-down menu to select a metric
                                        dbc.Row(
                                            dbc.Card(
                                                [
                                                    dbc.Row(
                                                        html.P("Select a metric below:")
                                                    ),
                                                    dbc.Row(
                                                        dcc.Dropdown(
                                                            id="metric-picker",
                                                            options=[
                                                                "Import",
                                                                "Export",
                                                                "Production",
                                                                "Consumption",
                                                                "Net Trade",
                                                                "Self-Sufficiency Ratio",
                                                            ],
                                                            value="Import",
                                                        )
                                                    ),
                                                ],
                                                className="mb-3",
                                            )
                                        ),
                                        # Drop-down menu to select a year
                                        dbc.Row(
                                            dbc.Card(
                                                [
                                                    dbc.Row(
                                                        html.P("Select a year below:")
                                                    ),
                                                    dbc.Row(
                                                        dcc.Dropdown(
                                                            id="year-picker",
                                                            options=data[
                                                                "Year"
                                                            ].unique(),
                                                            value=data["Year"].max(),
                                                        )
                                                    ),
                                                ],
                                                className="mb-3",
                                            )
                                        ),
                                        # A button to download raw data
                                        dbc.Row(
                                            html.Div(
                                                [
                                                    html.Button(
                                                        "Download All Data",
                                                        id="btn-download1",
                                                        className="btn btn-primary",
                                                    ),
                                                    dcc.Download(id="download-csv1"),
                                                ]
                                            ),
                                            className="h-100",
                                        ),
                                    ],
                                    width=2,
                                    className="h-100",
                                ),
                                # Middle column: World Map of the selected metric in selected year
                                dbc.Col(
                                    dbc.Card(
                                        dcc.Graph(id="global-map"), className="h-100"
                                    ),
                                    className="h-100",
                                ),
                                # Rightmost column: Global Average time series of the selected metric
                                dbc.Col(
                                    dbc.Card(
                                        dcc.Graph(id="global-time-series"),
                                        className="h-100",
                                    ),
                                    className="h-100",
                                ),
                            ],
                            align="stretch",
                        ),
                    ],
                ),
                # Tab 2: Continental Analysis
                dcc.Tab(
                    label="Continental Analysis",
                    value="tab2",
                    children=[
                        # Title of Tab 2
                        dbc.Row(
                            html.H1(
                                id="continent-title", style={"text-align": "center"}
                            )
                        ),
                        # Description of Tab 2
                        dbc.Row(
                            dbc.Col(
                                dbc.Card(
                                    [dbc.Row(html.P(id="description2"))],
                                    className="mb-3",
                                ),
                                width=9,
                            ),
                            justify="center",
                        ),
                        # Contents of Tab 2
                        dbc.Row(
                            [
                                # Leftmost column: interactive element (one drop down menu)
                                dbc.Col(
                                    [
                                        # Drop-down menu to select a metric
                                        dbc.Row(
                                            dbc.Card(
                                                [
                                                    dbc.Row(
                                                        html.P("Select a metric below:")
                                                    ),
                                                    dbc.Row(
                                                        dcc.Dropdown(
                                                            id="metric-picker-2",
                                                            options=[
                                                                "Import",
                                                                "Export",
                                                                "Production",
                                                                "Consumption",
                                                            ],
                                                            value="Import",
                                                        )
                                                    ),
                                                ],
                                                className="mb-3",
                                            )
                                        ),
                                        # A button to download continental (wrangled) data
                                        dbc.Row(
                                            html.Div(
                                                [
                                                    html.Button(
                                                        "Download Continental Data",
                                                        id="btn-download2",
                                                        className="btn btn-primary",
                                                    ),
                                                    dcc.Download(id="download-csv2"),
                                                ]
                                            ),
                                            className="h-100",
                                        ),
                                    ],
                                    width=2,
                                    className="h-100",
                                ),
                                # Middle column: How each continent’s percentage of
                                # global total for the selected spice metric changes across the years
                                dbc.Col(
                                    dbc.Card(
                                        dcc.Graph(id="continent-stacked-area"),
                                        className="h-100",
                                    ),
                                    className="h-100",
                                ),
                                # Rightmost column: Continental total of the selected spice metric
                                # in the hovered year
                                dbc.Col(
                                    dbc.Card(
                                        dcc.Graph(id="continent-bar-chart"),
                                        className="h-100",
                                    ),
                                    className="h-100",
                                ),
                            ],
                            align="stretch",
                        ),
                    ],
                ),
                # Tab 3: Country-level Dive
                dcc.Tab(
                    label="Country-level Dive",
                    value="tab3",
                    children=[
                        # Title of Tab 3
                        dbc.Row(
                            html.H1(id="country-title", style={"text-align": "center"})
                        ),
                        # Description of Tab 3
                        dbc.Row(
                            dbc.Col(
                                dbc.Card(
                                    [dbc.Row(html.P(id="description3"))],
                                    className="mb-3",
                                ),
                                width=9,
                            ),
                            justify="center",
                        ),
                        # Contents of Tab 3
                        dbc.Row(
                            [
                                # Leftmost column: interactive elements
                                # (two drop down menus, one range slider)
                                dbc.Col(
                                    [
                                        # multi-drop down menu to select countries
                                        dbc.Row(
                                            dbc.Card(
                                                [
                                                    dbc.Row(
                                                        html.P(
                                                            "Select a country / countries below:"
                                                        )
                                                    ),
                                                    dbc.Row(
                                                        dcc.Dropdown(
                                                            id="country-picker",
                                                            options=data[
                                                                "Area"
                                                            ].unique(),
                                                            multi=True,
                                                        )
                                                    ),
                                                ],
                                                className="mb-3",
                                            )
                                        ),
                                        # single drop down menu to select metric
                                        dbc.Row(
                                            dbc.Card(
                                                [
                                                    dbc.Row(
                                                        html.P("Select a metric below:")
                                                    ),
                                                    dbc.Row(
                                                        dcc.Dropdown(
                                                            id="metric-picker-3",
                                                            options=[
                                                                "Import",
                                                                "Export",
                                                                "Production",
                                                                "Consumption",
                                                                "Net Trade",
                                                                "Self-Sufficiency Ratio",
                                                            ],
                                                            value="Import",
                                                        )
                                                    ),
                                                ],
                                                className="h-100 mb-3",
                                            )
                                        ),
                                        # input boxes to enter the start and end year
                                        dbc.Row(
                                            dbc.Card(
                                                [
                                                    dbc.Row(
                                                        html.P(
                                                            "Select start/end year below:"
                                                        )
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                dcc.Input(
                                                                    id="start-year",
                                                                    type="number",
                                                                    min=data[
                                                                        "Year"
                                                                    ].min(),
                                                                    max=data[
                                                                        "Year"
                                                                    ].max()
                                                                    - 1,
                                                                    step=1,
                                                                    value=1993,
                                                                    placeholder="Start Year",
                                                                    className="form-control",
                                                                )
                                                            ),
                                                            dbc.Col(
                                                                dcc.Input(
                                                                    id="end-year",
                                                                    type="number",
                                                                    min=1994,
                                                                    max=data[
                                                                        "Year"
                                                                    ].max(),
                                                                    step=1,
                                                                    value=2023,
                                                                    placeholder="End Year",
                                                                    className="form-control",
                                                                )
                                                            ),
                                                        ]
                                                    ),
                                                    # outputs a warning if end year < start year
                                                    dbc.Row(
                                                        html.Div(
                                                            id="year-warning",
                                                            style={
                                                                "color": "red",
                                                                "fontWeight": "bold",
                                                                "marginTop": "5px",
                                                            },
                                                        )
                                                    ),
                                                ],
                                                className="mb-3",
                                            )
                                        ),
                                        # A button to download world rank data
                                        dbc.Row(
                                            html.Div(
                                                [
                                                    html.Button(
                                                        "Download World Rank Data",
                                                        id="btn-download3",
                                                        className="btn btn-primary",
                                                    ),
                                                    dcc.Download(id="download-csv3"),
                                                ]
                                            ),
                                            className="h-100",
                                        ),
                                    ],
                                    width=2,
                                    className="h-100",
                                ),
                                # Middle column: Time series plot of the selected countries
                                # between selected years in terms of selected metric
                                dbc.Col(
                                    dbc.Card(
                                        dcc.Graph(id="country-time-series"),
                                        className="h-100",
                                    ),
                                    className="h-100",
                                ),
                                # Rightmost column: Time series plot of the selected countries
                                # between selected years in terms of the country's world rank
                                dbc.Col(
                                    dbc.Card(
                                        dcc.Graph(id="country-world-rank"),
                                        className="h-100",
                                    ),
                                    className="h-100",
                                ),
                            ],
                            align="stretch",
                        ),
                    ],
                ),
                # Tab 4: Top-5 Countries within a certain year and scope
                dcc.Tab(
                    label="Top-5 Countries",
                    value="tab4",
                    children=[
                        # Title of Tab 4
                        dbc.Row(
                            html.H1(id="top5-title", style={"text-align": "center"})
                        ),
                        # Contents of Tab 4
                        dbc.Row(
                            [
                                # Leftmost column: interactive elements
                                # (three drop down menus)
                                dbc.Col(
                                    [
                                        # drop down menu to pick metric
                                        dbc.Row(
                                            dbc.Card(
                                                [
                                                    dbc.Row(
                                                        html.P("Select a metric below:")
                                                    ),
                                                    dbc.Row(
                                                        dcc.Dropdown(
                                                            id="metric-picker-4",
                                                            options=[
                                                                "Import",
                                                                "Export",
                                                                "Production",
                                                                "Consumption",
                                                            ],
                                                            value="Import",
                                                        )
                                                    ),
                                                ],
                                                className="mb-3",
                                            )
                                        ),
                                        # drop down menu to pick year
                                        dbc.Row(
                                            dbc.Card(
                                                [
                                                    dbc.Row(
                                                        html.P("Select a year below:")
                                                    ),
                                                    dbc.Row(
                                                        dcc.Dropdown(
                                                            id="year-picker-2",
                                                            options=data[
                                                                "Year"
                                                            ].unique(),
                                                            value=data["Year"].max(),
                                                        )
                                                    ),
                                                ],
                                                className="h-100 mb-3",
                                            )
                                        ),
                                        # drop down menu to pick comparison scope
                                        dbc.Row(
                                            dbc.Card(
                                                [
                                                    dbc.Row(
                                                        html.P(
                                                            "Select the scope of comparison below:"
                                                        )
                                                    ),
                                                    dbc.Row(
                                                        dcc.Dropdown(
                                                            id="scope-picker",
                                                            options=[
                                                                "Africa",
                                                                "America",
                                                                "Asia",
                                                                "Europe",
                                                                "Oceania",
                                                                "the Whole World",
                                                            ],
                                                            value="the Whole World",
                                                        )
                                                    ),
                                                ],
                                                className="mb-3",
                                            )
                                        ),
                                    ],
                                    width=2,
                                    className="h-100",
                                ),
                                # Middle column: Bar chart of top 5 countries in terms of
                                # the selected metric in selected year within the selected scope
                                dbc.Col(
                                    dbc.Card(
                                        dcc.Graph(id="top5-bar-chart"),
                                        className="h-100",
                                    ),
                                    className="h-100",
                                ),
                                # Rightmost column: A summary table of the market share
                                # of these 5 countries
                                dbc.Col(
                                    [
                                        dbc.Row(
                                            html.P(
                                                id="market-share-title",
                                                className="text-center",
                                            )
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Card(
                                                            "Rank", style=card_style
                                                        ),
                                                        dbc.Card("1", style=card_style),
                                                        dbc.Card("2", style=card_style),
                                                        dbc.Card("3", style=card_style),
                                                        dbc.Card("4", style=card_style),
                                                        dbc.Card("5", style=card_style),
                                                    ]
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Card(
                                                            "Country Name",
                                                            style=card_style,
                                                        ),
                                                        dbc.Card(
                                                            id="top1-country-name",
                                                            style=card_style,
                                                        ),
                                                        dbc.Card(
                                                            id="top2-country-name",
                                                            style=card_style,
                                                        ),
                                                        dbc.Card(
                                                            id="top3-country-name",
                                                            style=card_style,
                                                        ),
                                                        dbc.Card(
                                                            id="top4-country-name",
                                                            style=card_style,
                                                        ),
                                                        dbc.Card(
                                                            id="top5-country-name",
                                                            style=card_style,
                                                        ),
                                                    ]
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Card(
                                                            id="column-name-market-share",
                                                            style=card_style,
                                                        ),
                                                        dbc.Card(
                                                            id="top1-market-share",
                                                            style=card_style,
                                                        ),
                                                        dbc.Card(
                                                            id="top2-market-share",
                                                            style=card_style,
                                                        ),
                                                        dbc.Card(
                                                            id="top3-market-share",
                                                            style=card_style,
                                                        ),
                                                        dbc.Card(
                                                            id="top4-market-share",
                                                            style=card_style,
                                                        ),
                                                        dbc.Card(
                                                            id="top5-market-share",
                                                            style=card_style,
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                    ]
                                ),
                            ],
                            align="stretch",
                        ),
                    ],
                ),
            ],
        )
    ]
)


# Call back function of Tab 1
@app.callback(
    Output("global-title", "children"),
    Output("description", "children"),
    Output("global-map", "figure"),
    Output("global-time-series", "figure"),
    Output("download-csv1", "data"),
    Input("metric-picker", "value"),
    Input("year-picker", "value"),
    Input("btn-download1", "n_clicks"),
)
def global_overview_plots(metric, year, n_clicks):

    # Title of Tab 1
    title = f"Global Overview of Spice {metric}"

    # Description of Tab 1
    description = """As essential ingredients and commodities, the production, consumption, 
    and global trade of spices are of vital importance to everyday life and the global 
    economy, which are the key themes this dashboard aims to illustrate graphically.

    This tab provides a global overview of spice imports, exports, production, consumption,
    net trade and self-sufficiency ratio for a selected year, as well as the global trend of
    the chosen metric across multiple years. 

    The data used ranges from 1993 to 2023."""

    # Tab 1 visualization 1: World Map of the selected metric in selected year
    global_map = (
        px.choropleth(
            (data[data["Year"] == year].sort_values("Year")),
            locations="ISO-3",
            color=metric,
            animation_frame="Year",
            locationmode="ISO-3",
            hover_data={"Area": True, metric: True, "Year": True, "ISO-3": False},
        )
        .update_geos(fitbounds="locations")
        .update_layout(
            margin={"r": 0, "t": 40, "l": 0, "b": 100}, coloraxis_colorbar_x=0.85
        )
        .update_layout(
            coloraxis=dict(
                cmin=data[data["Year"] == year][metric].quantile(0.03),
                cmax=data[data["Year"] == year][metric].quantile(0.97),
                colorbar=dict(
                    orientation="h", xanchor="center", yanchor="top", x=0.5, y=-0.15
                ),
            ),
            title=dict(
                text=f"World Map of Spice {metric} in {year}",
                xanchor="center",
                yanchor="top",
                x=0.5,
            ),
        )
    )

    # Tab 1 visualization 2: Global Average time series of the selected metric
    global_time_series = (
        px.line(
            (data.groupby("Year")[metric].mean().to_frame().reset_index()),
            x="Year",
            y=metric,
        )
        .update_layout(
            title=dict(
                text=f"World Average of Spice {metric} across years",
                xanchor="center",
                yanchor="top",
                x=0.5,
            )
        )
        .update_yaxes(title_text=f"World Average {metric}")
    )

    # The button to download all data
    if ctx.triggered_id == "btn-download1":
        download_df = dcc.send_data_frame(data.to_csv, "map_data.csv", index=False)
    else:
        download_df = no_update

    return title, description, global_map, global_time_series, download_df


# First call back function of Tab 2
@app.callback(
    Output("continent-title", "children"),
    Output("description2", "children"),
    Output("continent-stacked-area", "figure"),
    Output("download-csv2", "data"),
    Input("metric-picker-2", "value"),
    Input("btn-download2", "n_clicks"),
)
def continent_analysis_plots(metric, n_clicks):

    # Title of Tab 2
    title = f"Continental Analysis of Spice {metric}"

    # Description of Tab 2
    description2 = """This tab shows how these five continents (Africa,
    America, Asia, Europe, Oceania) contribute to the global total of 
    the selected spice metric in percentage terms. When hovering
    over the boundary line that separates any two continents in the first plot,
    the raw values of the selected spice metric for that hovered year
    across all five continents will appear as a bar chart in the second plot."""

    # Processed data frame for plotting
    plot_df = data.groupby(["Continent", "Year"]).agg({metric: "sum"}).reset_index()

    # Tab 2 visualization 1: Stacked area chart showing continental percentage compared to world total
    continent_stacked_area = (
        px.area(plot_df, x="Year", y=metric, color="Continent", groupnorm="percent")
        .update_layout(
            title=dict(
                text=(
                    f"Continental Percentage of World Total <br>"
                    f"Spice {metric} across years"
                ),
                xanchor="center",
                yanchor="top",
                x=0.5,
            )
        )
        .update_yaxes(title_text=f"Percentage of World Total Spice {metric}")
        .update_traces(
            hovertemplate=(
                "Continent: %{fullData.name}<br>"
                "Year: %{x}<br>"
                "Percentage: %{y:.2f}%<extra></extra>"
            )
        )
    )

    # Prepare dataframe to download
    continental_df = (
        data.groupby(["Continent", "Year"])
        .agg(
            {
                "Import": "sum",
                "Export": "sum",
                "Production": "sum",
                "Consumption": "sum",
            }
        )
        .reset_index()
    )

    # A button to download continental data
    if ctx.triggered_id == "btn-download2":
        download_df = dcc.send_data_frame(
            continental_df.to_csv, "continental_data.csv", index=False
        )
    else:
        download_df = no_update

    return title, description2, continent_stacked_area, download_df


# Second call back function of Tab 2 (Cross-Filtering)
@app.callback(
    Output("continent-bar-chart", "figure"),
    Input("metric-picker-2", "value"),
    Input("continent-stacked-area", "hoverData"),
)
def continent_analysis_plots2(metric, hoverData):

    # No updates on the second chart if there is no hover data
    if hoverData is None:
        raise PreventUpdate

    # Processed data frame for plotting
    plot_df = data.groupby(["Continent", "Year"]).agg({metric: "sum"}).reset_index()

    # Tab 2 visualization 2: Bar chart showing continental total of
    # the selected metric in the hovered year
    continent_bar_chart = px.bar(
        plot_df[plot_df["Year"] == hoverData["points"][0]["x"]],
        x=metric,
        y="Continent",
        color="Continent",
        opacity=0.6,
    ).update_layout(
        title=dict(
            text=f"Total Spice {metric} in each continent in {hoverData['points'][0]['x']}",
            xanchor="center",
            yanchor="top",
            x=0.5,
        )
    )

    return continent_bar_chart


# Call back function of Tab 3
@app.callback(
    Output("country-title", "children"),
    Output("description3", "children"),
    Output("country-time-series", "figure"),
    Output("country-world-rank", "figure"),
    Output("year-warning", "children"),
    Output("download-csv3", "data"),
    Input("country-picker", "value"),
    Input("metric-picker-3", "value"),
    Input("start-year", "value"),
    Input("end-year", "value"),
    Input("btn-download3", "n_clicks"),
)
def country_level_plots(countries, metric, start_year, end_year, n_clicks):

    # Title of Tab 3
    title = f"Country-level Deep Dive of Spice {metric}"

    # Description of Tab 3
    description3 = """This tab demonstrates country-level values of 
    the selected spice metric across the selected years in the first plot.
    More specifically, selected countries are compared against one another,
    each as a uniquely colored line. In the second line chart, the same
    selected countries are compared in terms of their world rank for this 
    chosen metric over the selected time span.
    """

    # Default empty figures and warning
    empty_fig = {}
    warning = ""

    # Prepare world rank dataframe to download later
    world_rank_data = data.copy()
    metrics = [
        "Import",
        "Export",
        "Production",
        "Consumption",
        "Net Trade",
        "Self-Sufficiency Ratio",
    ]
    for metric in metrics:
        world_rank_data[metric + "_Rank"] = (
            world_rank_data.groupby("Year")[metric]
            .rank(method="min", ascending=False)
            .astype("Int64")
        )
    world_rank_data = world_rank_data[["Area", "Year"] + [m + "_Rank" for m in metrics]]

    # A button to download world rank data
    if ctx.triggered_id == "btn-download3":
        download_df = dcc.send_data_frame(
            world_rank_data.to_csv, "world_rank_data.csv", index=False
        )
    else:
        download_df = no_update

    # No updates on both charts if countries are not selected
    if countries is None or start_year is None or end_year is None:
        return title, description3, empty_fig, empty_fig, warning, download_df

    # Outputs a warning message if end year is earlier than start year
    if end_year <= start_year:
        warning = "End year must be greater than start year."
        return title, description3, empty_fig, empty_fig, warning, download_df

    # Tab 3 visualization 1: Time series plot of the selected countries
    # between selected years in terms of selected metric
    cond = (data["Area"].isin(countries)) & (
        data["Year"].isin(range(start_year, end_year + 1))
    )
    country_time_series = px.line(
        data[cond], x="Year", y=metric, color="Area"
    ).update_layout(
        title=dict(
            text=(
                f"Spice {metric} of selected countries <br>"
                f"between {start_year} and {end_year}"
            ),
            xanchor="center",
            yanchor="top",
            x=0.5,
        )
    )

    # Tab 3 visualization 2: Time series plot of the selected countries
    # between selected years in terms of the country's world rank of this metric
    data_with_world_rank = data.copy()
    data_with_world_rank["world_rank"] = (
        data_with_world_rank.groupby(["Year"])[metric]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    country_world_rank = (
        px.line(data_with_world_rank[cond], x="Year", y="world_rank", color="Area")
        .update_layout(
            title=dict(
                text=(
                    f"Country's World Rank of Spice {metric} <br>"
                    f"between {start_year} and {end_year}"
                ),
                xanchor="center",
                yanchor="top",
                x=0.5,
            )
        )
        .update_yaxes(title_text=f"World Rank of Spice {metric}")
    )

    return (
        title,
        description3,
        country_time_series,
        country_world_rank,
        warning,
        download_df,
    )


# Call back function of Tab 4
@app.callback(
    Output("top5-title", "children"),
    Output("top5-bar-chart", "figure"),
    Output("market-share-title", "children"),
    Output("top1-country-name", "children"),
    Output("top2-country-name", "children"),
    Output("top3-country-name", "children"),
    Output("top4-country-name", "children"),
    Output("top5-country-name", "children"),
    Output("column-name-market-share", "children"),
    Output("top1-market-share", "children"),
    Output("top2-market-share", "children"),
    Output("top3-market-share", "children"),
    Output("top4-market-share", "children"),
    Output("top5-market-share", "children"),
    Input("metric-picker-4", "value"),
    Input("year-picker-2", "value"),
    Input("scope-picker", "value"),
)
def top5_plot_and_table(metric, year, scope):

    # Title of Tab 4
    top5_title = f"Top 5 countries of {metric} in {year} within {scope}"

    # Get the data frame used for plotting
    # and calculate the market total
    if scope == "the Whole World":
        plot_df = (
            data[data["Year"] == year].sort_values(metric, ascending=False).iloc[:5, :]
        )
        market_total = data[data["Year"] == year][metric].sum()

    else:
        plot_df = (
            data[(data["Year"] == year) & (data["Continent"] == scope)]
            .sort_values(metric, ascending=False)
            .iloc[:5, :]
        )
        market_total = data[(data["Year"] == year) & (data["Continent"] == scope)][
            metric
        ].sum()

    # Tab 4 visualization 1: Bar chart
    top5_bar_chart = px.bar(
        plot_df.sort_values(metric, ascending=True), x=metric, y="Area"
    )

    # Tab 4 summary table: market share
    market_share_title = f"Market Share of {metric} of these 5 countries"
    top1_country_name = plot_df["Area"].iloc[0]
    top2_country_name = plot_df["Area"].iloc[1]
    top3_country_name = plot_df["Area"].iloc[2]
    top4_country_name = plot_df["Area"].iloc[3]
    top5_country_name = plot_df["Area"].iloc[4]

    column_name_market_share = f"{metric} Market Share"
    top1_market_share = f"{plot_df[metric].iloc[0] / market_total * 100:.2f}%"
    top2_market_share = f"{plot_df[metric].iloc[1] / market_total * 100:.2f}%"
    top3_market_share = f"{plot_df[metric].iloc[2] / market_total * 100:.2f}%"
    top4_market_share = f"{plot_df[metric].iloc[3] / market_total * 100:.2f}%"
    top5_market_share = f"{plot_df[metric].iloc[4] / market_total * 100:.2f}%"

    return (
        top5_title,
        top5_bar_chart,
        market_share_title,
        top1_country_name,
        top2_country_name,
        top3_country_name,
        top4_country_name,
        top5_country_name,
        column_name_market_share,
        top1_market_share,
        top2_market_share,
        top3_market_share,
        top4_market_share,
        top5_market_share,
    )


if __name__ == "__main__":
    app.run(jupyter_mode="external")
