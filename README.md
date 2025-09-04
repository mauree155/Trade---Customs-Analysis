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

## Project Overview
This project demonstrates how raw **trade and customs data** can be transformed into **actionable insights** for decision-makers.  

The workflow covers:
- Cleaning raw, inconsistent data  
- Exploring patterns and relationships through **Exploratory Data Analysis (EDA)**  
- Engineering business-relevant features such as compliance, taxation fairness, and timeliness  
- Building an **interactive dashboard** to monitor trade activities, taxation efficiency, and compliance  

The end result is a comprehensive data product that provides customs authorities, policymakers, and analysts with a clear view of trade flows, risks, and opportunities.  

## Business Problem
Customs agencies face several recurring challenges that hinder efficiency and revenue collection:

- **Delayed processing of imports** – long clearance times slow down trade flows.  
- **Inefficient or uneven taxation structures** – overreliance on product value while ignoring mass or container size.  
- **Dependency on limited partners** – a small number of countries and HS codes dominate trade.  
- **Compliance gaps in tax payment timelines** – late payments reduce cash flow and weaken accountability.  

Without structured analysis, these issues remain hidden within raw data.  
This project uses data analytics to uncover inefficiencies, identify risks, and highlight opportunities for reform.

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

## Workflow

### 1. Data Cleaning
The raw trade and customs dataset contained missing values, inconsistent naming conventions, incorrect dates, and potential outliers.  
The following steps were applied to prepare the data for analysis:  

- Removed irrelevant columns (e.g., `Unnamed`)  
- Renamed columns for clarity and consistency  
- Standardized country names using the `pycountry` library  
- Handled missing values with forward fill and replacement strategies  
- Converted date fields into proper `datetime` objects
- Created chapter, section & section_name columns based on the guidance offered by: https://github.com/datasets/harmonized-system/blob/main/data/harmonized-system.csv
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

view my charts <a href="https://github.com/mauree155/Trade-and-Customs-Analysis/tree/main/Charts">Here</a>

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

🔗 [View the Live Dashboard](https://trade-and-customs-analysis-awaq.onrender.com/)


## Findings and Insights

### 1. Country Dependence
- Imports are dominated by a few countries, with **China alone accounting for 40.37% of CIF value (≈ $778B)**.  
- Other major sources include **Lebanon (6.27%)**, **Italy (6.17%)**, **United Kingdom (6.09%)**, and **India (5.99%)**.  
- Combined, the **top 5 countries contribute over 65%** of total import value, showing high reliance on limited trade partners.  
- This level of concentration exposes customs revenue to risks from **geopolitical or economic shifts** in these countries.
  
```python
# Top 5 countries by CIF share
country_share = df.groupby("Country_of_origin")["CIF_value($)"].sum().nlargest(5)
country_share_percent = (country_share / df["CIF_value($)"].sum()) * 100
print(country_share_percent)
```


### 2. Product Categories (HS codes & sections)
- Imports are concentrated within a narrow set of product categories.  
- **HS Code 28721000 alone contributes 7.79% of imports (≈ $150B)**.
- Section VI (Chemicals & Allied Industries) is the largest, making up ≈ 22% of imports.
Section XI (Textiles and Textile Articles) and Section XVI (Machinery & Electrical
- The **top 5 HS codes collectively account for nearly 28%** of trade value.  
- This concentration means disruptions in just a few product classes would significantly impact trade revenue.
```python
# Top 5 HS codes by CIF value
hs_share = df.groupby("HS_code")["CIF_value($)"].sum().nlargest(5)
hs_share_percent = (hs_share /df["CIF_value($)"].sum()) * 100
print(hs_share_percent)

# Top sections by CIF value
section_share = df.groupby("section")["CIF_value($)"].sum().nlargest(5)
(section_share / df["CIF_value($)"].sum() * 100).round(2)
```

### 3. Taxation Efficiency
- Correlation analysis shows a **strong positive relationship (r = 0.72)** between **CIF value** and **Total Tax collected**.  
- This confirms that taxation is primarily **value-based (ad valorem)**.  
- However, a minority of shipments deviate from the trend, suggesting potential cases of **under-taxation, over-taxation, or misclassification**.  
- These anomalies highlight opportunities for **targeted auditing and compliance checks**.
```python
df["CIF_value($)"].corr(df["Total_Tax($)"])
```

### 4. Processing Timeliness
- The **average processing time** from registration to receipt is **4.5 days**.  
- While most shipments fall within the expected 7-day SLA, **19.9% of transactions exceeded 7 days**, pointing to inefficiencies.  
- Such delays increase importer costs and slow trade flows, signaling the need for operational reforms.
```python
df["Processing_Days"] = (df["Receipt_date"] - df["Reg_date"]).dt.days
df["Processing_Days"].mean(), (df["Processing_Days"] > 7).mean() * 100
```
### 5. Compliance Gaps
- On-time payment compliance stands at **80.1%**, while **19.9% of importers delayed tax payments** beyond due dates.  
- This suggests gaps in enforcement and an opportunity for **automated reminders, penalties, and compliance monitoring systems**.
```python
df["On_Time"] = df["Receipt_date"] <= df["Due_date"]
df["On_Time"].mean()
```
### 6. Seasonal and Temporal Trends
- Trade volumes show strong monthly variation.  
- CIF imports **peaked in January 2022 (≈ $355B)**, then **dropped to $96B in March 2022**.

- These fluctuations suggest **seasonal trade cycles** (festive periods, agriculture, or global demand shifts) that customs can leverage for **forecasting and resource planning**.
```python
monthly_cif = df.groupby(df["Reg_date"].dt.to_period("M"))["CIF_value($)"].sum()
monthly_cif
```

## Recommendations

1. **Diversify Trade Partnerships**  
   Reduce dependency on China and a few HS sections by creating trade incentives with other regions and strengthening local industries.  

2. **Review Taxation Policies**  
   Move beyond purely value-based taxation. Consider hybrid models that incorporate **mass** or **container size** to ensure balanced revenue collection.  

3. **Enhance Compliance Systems**  
   - Automate reminders and penalties for overdue tax payments.  
   - Introduce rewards or fast-track clearance for compliant importers.  

4. **Improve Processing Efficiency**  
   Use historical delay data to identify underperforming offices and digitize customs clearance to reduce bottlenecks.  

5. **Leverage Predictive Analytics**  
   Build models to forecast **seasonal trade spikes** and **revenue flows** to support proactive staffing, logistics, and budgeting.  


## How to Reproduce

Follow these steps to replicate the analysis:

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/your-username/trade-customs-analysis.git
   cd trade-customs-analysis
   Install Dependencies
   ```
2. Install Dependencies
```bash
pip install -r requirements.txt
```
3. Run the Analysis
```bash
Data Cleaning:
python cleaning.py
Exploratory Data Analysis (EDA):
python eda.py
Feature Engineering:
python feature_engineering.py
```
4. Launch Dashboard Locally
```bash
   dash-dashboard.py
```
5. View Deployed Dashboard
Access the live version here: [Dashboard Link](https://trade-and-customs-analysis-awaq.onrender.com/)

## Conclusion

This analysis of trade and customs data revealed several key insights:  

- Strong correlations exist between **FOB, CIF, and Total Tax**, confirming their central role in trade monitoring.  
- **China** and a few HS code sections dominate Nigeria’s imports, highlighting potential dependency risks.  
- Clear **seasonal and temporal trends** were observed, with trade volumes peaking around **festive and agricultural cycles**.  
- Tax contributions vary significantly across HS code sections, suggesting uneven revenue distribution.  
- Outlier transactions and irregular CIF-FOB ratios indicate areas where **compliance monitoring** can be strengthened.  

These findings underscore the importance of **data-driven customs management** to improve efficiency, reduce revenue leakages, and guide economic policy.  

## Contact

For questions, collaborations, or project discussions:

**Maureen Okoro**              
- 📨 [Email](mailto:okoromaureen590@gmail.com")
- 🌐 [GitHub](https://github.com/mauree155]
)
- 🔗 [LinkedIn](https://ng.linkedin.com/in/maureen-okoro-8a1972245)
