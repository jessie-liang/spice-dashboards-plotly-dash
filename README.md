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
