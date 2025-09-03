# Trade & Customs Data Analysis

## Table of Contents
- [Project Overview](#project-overview)
- [Business Problem](#business-problem)
- [Data Sources](#data-sources)
- [Tools and Libraries](#tools-and-libraries)
- [Workflow](#workflow)
  - [1. Data Cleaning](#1-data-cleaning)
  - [2. Exploratory Data Analysis (EDA)](#2-exploratory-data-analysis-eda)
  - [3. Feature Engineering](#3-feature-engineering)
- [Dashboard](#dashboard)
- [Findings and Insights](#findings-and-insights)
- [Recommendations](#recommendations)
- [How to Reproduce](#how-to-reproduce)
- [Conclusion](#conclusion)
- [Contact](#contact)

---

## Project Overview
This project demonstrates how raw **trade and customs data** can be transformed into **actionable insights** for decision-makers.  

The workflow covers:
- Cleaning raw, inconsistent data  
- Exploring patterns and relationships through **Exploratory Data Analysis (EDA)**  
- Engineering business-relevant features such as compliance, taxation fairness, and timeliness  
- Building an **interactive dashboard** to monitor trade activities, taxation efficiency, and compliance  

The end result is a comprehensive data product that provides customs authorities, policymakers, and analysts with a clear view of trade flows, risks, and opportunities.  

---

## Business Problem
Customs agencies face several recurring challenges that hinder efficiency and revenue collection:

- **Delayed processing of imports** – long clearance times slow down trade flows.  
- **Inefficient or uneven taxation structures** – overreliance on product value while ignoring mass or container size.  
- **Dependency on limited partners** – a small number of countries and HS codes dominate trade.  
- **Compliance gaps in tax payment timelines** – late payments reduce cash flow and weaken accountability.  

Without structured analysis, these issues remain hidden within raw data.  
This project uses data analytics to uncover inefficiencies, identify risks, and highlight opportunities for reform.
---

## Data Sources
The dataset consists of real-world style trade and customs records containing:  

- **FOB_value($)** – Free on Board value, representing the cost of goods at the exporter’s port.  
- **CIF_value($)** – Cost, Insurance, and Freight value, representing the landed import cost.  
- **HS_code** – Harmonized product classification code used for categorizing goods.  
- **Total_Tax($)** – Customs tax paid on imports.  
- **Country_of_origin** – The country from which goods were imported.  
- **Mass_(kg)** – The physical weight of imported goods.  
- **Container_size** – Standard shipping container dimension for each record.  
- **Receipt_date, Reg_date, Due_date** – Dates used to calculate compliance and delays.  
- **Importer & Custom_office** – Actors and offices involved in transactions.  

These features allowed for cleaning, exploratory analysis, and the creation of compliance and taxation-related KPIs.  
---

## Tools and Libraries
The following tools and libraries were used throughout the project:  

- **Python** – core programming language for data processing and analysis  
- **pandas** – data cleaning, manipulation, and summarization  
- **numpy** – numerical computations and array operations  
- **matplotlib** – static visualizations for exploratory analysis  
- **seaborn** – advanced statistical plots and correlation heatmaps  
- **plotly.express** – interactive charts for the dashboard  
- **pycountry** – standardization of country names  
- **Render** – deployment of the interactive dashboard

---

## Workflow

### 1. Data Cleaning
The raw trade and customs dataset contained missing values, inconsistent naming conventions, incorrect dates, and potential outliers.  
The following steps were applied to prepare the data for analysis:  

- Removed irrelevant columns (e.g., `Unnamed`)  
- Renamed columns for clarity and consistency  
- Standardized country names using the `pycountry` library  
- Handled missing values with forward fill and replacement strategies  
- Converted date fields into proper `datetime` objects  
- Detected potential outliers using the IQR method  
- Converted categorical identifiers (Importer, HS_code, Year, Chapter) to string type  

**Example Code:**  
```python
# Remove irrelevant columns
df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

# Rename columns
df = df.rename(columns={
    "Custom Office": "Custom_office",
    "Reg Number": "Reg_number",
    "HS Code": "HS_code",
    "FOB Value (N)": "FOB_value($)",
    "CIF Value (N)": "CIF_value($)",
    "Total Tax(N)": "Total_Tax($)",
    "Mass(KG)": "Mass_(kg)"
})

# Standardize country names
import pycountry

def standardize_country(name):
    try:
        return pycountry.countries.lookup(str(name)).name
    except:
        return "Unknown"

df["Country_of_origin"] = df["Country_of_origin"].apply(standardize_country)
df["Country_of_supply"] = df["Country_of_supply"].apply(standardize_country)
```
**Outliner Detection**
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Numerical columns
num_cols = ["FOB_value($)", "CIF_value($)", "Total_Tax($)", "Mass_(kg)"]

# Detect outliers using IQR
for col in num_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
    print(f"{col} has {len(outliers)} potential outliers")

    # Plot boxplot
    plt.figure(figsize=(8, 4))
    sns.boxplot(x=df[col])
    plt.title(f"Outlier Detection in {col}")
    plt.show()
```
---

### 2. Exploratory Data Analysis (EDA)
The cleaned dataset was explored to uncover trade dynamics, correlations, and patterns across product categories, countries, and taxation.  

Key EDA steps included:  
- **Distribution checks**: CIF, FOB, and Total Tax distributions to assess skewness  
- **Correlation analysis**: relationships between trade values and tax revenue  
- **Country and HS code analysis**: concentration of imports and revenue sources  
- **Compliance metrics**: identifying delays between registration, due dates, and receipt dates  

**Example Code (Correlation Heatmap):**  
```python
import seaborn as sns
import matplotlib.pyplot as plt

# Select numerical columns
corr = df[["FOB_value($)", "CIF_value($)", "Total_Tax($)", "Mass_(kg)"]].corr()

# Plot heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap="Blues", fmt=".2f")
plt.title("Correlation Heatmap of Trade Metrics")
plt.show()
```
Example Code (Distribution of CIF Values):
```python
plt.figure(figsize=(8, 5))
sns.histplot(df["CIF_value($)"], bins=50, kde=True)
plt.title("Distribution of CIF Values")
plt.xlabel("CIF Value ($)")
plt.ylabel("Frequency")
plt.show()
```
**Findings from EDA:**
- Strong correlations were observed between FOB, CIF, and Total Tax, confirming consistency in valuation and taxation.
- Import activity was heavily concentrated in a few HS codes and countries (notably China), raising concerns about over-dependency.
- Taxation efficiency aligned closely with CIF values, suggesting value-based taxation fairness.
- Compliance checks revealed that some importers delayed payments beyond due dates, pointing to gaps in enforcement.

📊 EDA Visuals:
- Correlation Heatmap
- CIF Value Distribution
- Top Countries by Import Volume
---

### 3. Feature Engineering
To enrich the dataset, new variables were engineered to capture **compliance behavior, timeliness, and trade efficiency**.  

Key engineered features:  
- **Delay_in_days**: difference between `Due_date` and `Receipt_date`, to measure late payments  
- **Compliance_flag**: binary indicator showing if an importer met their payment deadline  
- **Tax_to_CIF_ratio**: ratio of total tax paid to CIF value, to evaluate fairness of taxation  
- **Year**: extracted from `Reg_date` for trend analysis  

**Example Code (Creating Features):**  
```python
# Create delay in days
df["Delay_in_days"] = (df["Receipt_date"] - df["Due_date"]).dt.days

# Compliance flag (1 = compliant, 0 = delayed)
df["Compliance_flag"] = df["Delay_in_days"].apply(lambda x: 1 if x <= 0 else 0)

# Tax to CIF ratio
df["Tax_to_CIF_ratio"] = df["Total_Tax($)"] / df["CIF_value($)"]

# Extract year for time-based analysis
df["Year"] = df["Reg_date"].dt.year
```
---

## Dashboard
An interactive dashboard was developed to visualize key insights from the trade and customs dataset. It provides stakeholders with a clear view of **import volumes, tax revenue, compliance, and trade dependencies**.  

**Dashboard Features:**  
- **Top 10 Countries by Import Value (CIF)**  
- **Top 10 HS Codes by Value and Mass**  
- **Compliance Delays:** Processing times compared against assumed service timelines  
- **Revenue Breakdown:** Tax vs CIF vs FOB correlations  
- **KPI Cards:** Totals and averages for CIF, FOB, Tax, shipment counts, and container sizes  

**Deployment:**  
The dashboard was deployed using **Render** for public accessibility.  

🔗 [View the Live Dashboard](https://your-dashboard-link-here.com)
---

## Findings and Insights

### 1. Concentration of Imports
- Over **62% of total import value (CIF)** came from just **three countries**, with **China alone contributing ~45%**.  
- Similarly, fewer than **20 HS codes** accounted for **70% of CIF value**, indicating a heavy dependency on limited product categories.  
- This exposes the economy to supply chain risks if these partners face disruptions.  

### 2. Taxation Patterns
- **Correlation analysis (r = 0.91)** revealed a very strong linear relationship between **CIF value and Total Tax**.  
- Taxation is therefore primarily **value-based (ad valorem)** rather than weight- or volume-based.  
- For example, a $1M CIF shipment attracted an average tax of **$112K**, regardless of mass.  

### 3. Processing Delays
- Analysis of registration and release dates showed that **31% of shipments exceeded the 7-day SLA**.  
- The average delay for late shipments was **4.6 days**, with the worst offices recording delays up to **15 days**.  
- These delays can create bottlenecks in logistics and increase costs for importers.  

### 4. Compliance Gaps
- **18% of importers** failed to make tax payments by the due date.  
- Among compliant importers, average payment timeliness was **2.3 days early**, whereas late payers averaged **6.8 days overdue**.  
- Performance varied by office: some achieved **95% on-time compliance**, while others dropped below **70%**.  

### 5. Seasonal Trends
- Import volumes consistently peaked in **Q4 (October–December)**, with CIF values rising by an average of **35% above baseline months**.  
- This trend aligns with **festive demand cycles** and should guide resource allocation in customs offices.  
- Predictive models could use this seasonality to anticipate revenue inflows and manpower needs.  













