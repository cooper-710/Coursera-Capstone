# SpaceX Falcon 9 Landing Prediction

This repository contains my final project for the IBM Data Science Capstone. The project analyzes SpaceX Falcon 9 launch data to understand factors that influence first-stage landing success and builds classification models to predict launch outcomes.

## Project Overview

SpaceX reduces launch costs by recovering and reusing the Falcon 9 first stage. This project uses launch data to explore which variables are associated with successful landings and whether machine learning models can predict landing success.

## Main Questions

- Which launch sites have the strongest success patterns?
- How do payload mass, orbit type, and flight number relate to landing success?
- Can classification models predict whether the Falcon 9 first stage will land successfully?

## Repository Structure

- `notebooks/` contains all completed Jupyter notebooks.
- `dashboard/` contains the Plotly Dash dashboard app.
- `images/` contains charts, maps, dashboard screenshots, and model results.
- `data/` contains datasets used or created during the project.
- `final_report/` contains the final submitted PDF report.

## Methods Used

- Data collection with SpaceX API
- Web scraping
- Data wrangling with pandas
- Exploratory data analysis
- SQL analysis
- Folium interactive mapping
- Plotly Dash dashboard development
- Classification modeling

## Models Tested

- Logistic Regression
- Support Vector Machine
- Decision Tree
- K-Nearest Neighbors

## Final Deliverable

The final report is submitted as a PDF presentation named:

`Data Science Capstone Project Report.pdf`
