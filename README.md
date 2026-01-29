# Dashboard of spice data analysis

## About

Spices play an indispensable role in people’s daily lives, 
thanks to their distinctive flavors and the enjoyment they bring. 
Beyond their taste and aroma, spices have been valued for their 
cultural and medicinal significance, both historically and today. 
As essential ingredients and commodities, their production, consumption, 
and global trade are of vital importance to our everyday life and the 
global economy, which are the key metrics this dashboard aims to illustrate graphically. 

## View the end product

Please find the published version of this dashboard here:
<https://jessieliang.pythonanywhere.com>

When viewing the dashboard, please make sure the browser window is large enough
(full screen is recommended), so that the contents can be displayed properly.

## Introduction to each tab

### Tab 1: Global Overview

This tab provides a global overview of spice imports, exports, production, consumption, 
net trade and self-sufficiency ratio for a selected year, as well as the global trend 
of the chosen metric across all available years. The data used ranges from 1993 to 2023.

- The interactive panel is in the leftmost column: two dropdown lists to select metric & year,
and a clickable button to download the raw data (the source data without manipulation).
- The first plot (global map) will be updated if either the metric or the year is changed.
- The second line chart only depends on the metric, and will not be updated if only the input
year is changed.

**Interesting findings**:

- Global import and export have been increasing over the years.
- Global production and consumption encountered a noticeable drop in 2014 and 2015, which matched
the happening time of El Nino, though the root cause still needs to be examined more thoroughly.
- Global net trade and self-sufficiency ratio are quite volatile.

### Tab 2: Continental Analysis

This tab shows how these five continents (Africa, America, Asia, Europe, Oceania) 
contribute to the global total of the selected spice metric in percentage terms. 
When hovering over the boundary line that separates any two continents in the 
first plot, the raw values of the selected spice metric for that hovered year 
across all five continents will appear as a bar chart in the second plot.

- Only the metric can be selected.
- The clickable button will download an aggregated dataset showing the import,
export, production and consumption data per continent per year.

**Interesting findings**:

- Asia is consistently the biggest spice consumer and producer.
- Europe, Asia and America are the major spice importers and exporters.
- Oceania accounts for the smallest proportion for all four metrics.

### Tab 3: Country-level Dive

This tab demonstrates country-level values of the selected spice metric 
across the selected years in the first plot. More specifically, selected countries 
are compared against one another, each as a uniquely colored line. 
In the second line chart, the same selected countries are compared in terms of 
their world rank for this chosen metric over the selected time span.

- One or more than one countries can be selected.
- Only one metric is selectable.
- Start/end year can be typed in the input boxes. If start year is later than
end year, a red error message will appear and plots cannot be generated.

**Feel free to compare any countries you're interested in!**

### Tab 4: Top-5 Countries

Based on the selected metric, year, and the comparison scope, a bar chart
of the top 5 countries is shown as the first visual, displaying the raw values
of this selected metric in the selected year and scope. A summary table on the
right-hand-side will demonstrate the numeric market share of these top five countries
in terms of the selected metric within the selected year and scope.

- Only one metric, year and comparison scope can be selected

**Use it for discovering the top 5 giants!**

## Run source code

### Step 1: Clone the repo

Run the following command in bash terminal:

```bash
git clone https://github.com/jessie-liang/spice-dashboards-plotly-dash.git
```

Then change the working directory to this cloned repo using `cd`.

### Step 2: Environment setup

Using environment.yml, run the following code in bash terminal:

```bash
conda env create -f environment.yml
conda activate plotly_dash_env
```

Then the environment called `plotly_dash_env` will be created and activated.

### Step 3: Run the analysis code

#### Way 1: run it in jupyter lab

Double check the current directory is the root directory of this project. Then
run 

```bash
jupyter lab
```

to open the jupyter lab in your browser. Then locate to `source_code.ipynb` under `src/` folder,
click "restart kernel and run all cells" in jupyter lab. At the end of the notebook, a link
will be generated: <http://127.0.0.1:8050> Click this link and the generated dashboard will be shown.

#### Way 2: run it in terminal

Double check the current directory is the root directory of this project, and the environment
`plotly_dash_env` has been activated. Then it the bash terminal, run the following code:

```bash
python src/source_code.py
```

A link will also be generated: <http://127.0.0.1:8050/> Copy this link to a browser and the dashboard will be shown.

## Source dataset

Source: <https://www.kaggle.com/datasets/harishthakur995/global-spice-consumption>

## Author

### Jessie Liang

- **Email**: <rnliang.jessie@gmail.com>
- **GitHub**: [@jessie-liang](https://github.com/jessie-liang)
