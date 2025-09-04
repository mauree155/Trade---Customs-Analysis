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

# Trade and Customs Data Analysis Project

## Project Overview

In the modern trade landscape, customs authorities handle massive volumes of data daily, from shipment details to taxation records. Yet, this data is often fragmented, inconsistent, and underutilized, leaving decision-makers without a clear picture of trade flows, compliance risks, and taxation efficiency.

This project demonstrates how trade and customs data can be transformed into actionable insights. By following a structured workflow involving data cleaning, exploratory analysis, feature engineering, and interactive dashboarding, raw data is turned into a comprehensive, decision-ready data product.

## Business Problem
Customs agencies face several recurring challenges that hinder efficiency and revenue collection:

- **Delayed processing of imports** – long clearance times slow down trade flows.  
- **Inefficient or uneven taxation structures** – overreliance on product value while ignoring mass or container size.  
- **Dependency on limited partners** – a small number of countries and HS codes dominate trade.  
- **Compliance gaps in tax payment timelines** – late payments reduce cash flow and weaken accountability. 

These challenges can lead to revenue loss, regulatory risks, and missed opportunities for optimizing trade operations.

## Aim

This project aims to unlock actionable insights from trade and customs data, enabling authorities and analysts to monitor trade activities, assess compliance, and make informed decisions that strengthen revenue collection and operational efficiency.

## Objectives

To achieve this aim, the project focuses on the following objectives:  
1. Data Cleaning – Transform raw, inconsistent trade and customs data into a reliable, analysis-ready format.  
2. Exploratory Data Analysis – Identify patterns, trends, and relationships across trade volumes, taxation, and compliance metrics.  
3. Feature Engineering – Create business-relevant metrics such as compliance scores, taxation fairness indicators, and shipment timeliness.  
4. Dashboard Development – Build an interactive tool that visualizes trade flows, taxation efficiency, and compliance, supporting real-time decision-making.  
5. Actionable Insights – Provide clear, data-driven recommendations to improve revenue collection, streamline operations, and mitigate risks.

 
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
- A few countries heavily dominate imports. China alone accounts for 40.37% of CIF value, approximately $778 billion. Other significant sources include Lebanon (6.27%), Italy (6.17%), the United Kingdom (6.09%), and India (5.99%).  
- Combined, the top five countries contribute over 65% of the total import value, highlighting a strong dependence on a limited set of trade partners.  
- This concentration exposes customs revenue to external risks, such as geopolitical tensions, trade restrictions, or economic instability in these key countries. It also emphasizes the need for diversification strategies to reduce vulnerability and ensure stable trade revenue streams.
  
```python
# Top 5 countries by CIF share
country_share = df.groupby("Country_of_origin")["CIF_value($)"].sum().nlargest(5)
country_share_percent = (country_share / df["CIF_value($)"].sum()) * 100
print(country_share_percent)
```


### 2. Product Categories (HS codes & sections)
Imports are concentrated in a small set of product categories. For example, HS Code 28721000 alone contributes 7.79% of imports, roughly $150 billion.

Section VI (Chemicals and Allied Industries) is the largest category, making up around 22% of total imports, followed by Section XI (Textiles and Textile Articles) and Section XVI (Machinery and Electrical Equipment).

The top five HS codes collectively account for nearly 28% of total trade value. This concentration indicates that any disruption in these product categories due to supply chain issues, regulatory changes, or global demand shifts could significantly impact trade revenue.

Understanding which categories dominate trade allows customs to prioritize monitoring and risk management for high-value sectors.
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
Correlation analysis shows a strong positive relationship (r = 0.72) between CIF value and total tax collected, indicating that taxation is largely value-based (ad valorem).

Despite this overall trend, a minority of shipments deviate significantly, pointing to potential under-taxation, over-taxation, or misclassification.

These deviations highlight areas where targeted audits, enhanced verification, or automated checks could improve revenue accuracy and ensure compliance.
```python
df["CIF_value($)"].corr(df["Total_Tax($)"])
```

### 4. Processing Timeliness
The average processing time from registration to receipt is 4.5 days, which is generally within the expected 7-day service level agreement.

However, approximately 19.9% of transactions exceeded 7 days, indicating inefficiencies in customs processing.

Delays increase costs for importers, slow down trade flows, and may affect overall operational efficiency. Addressing these bottlenecks could improve customer satisfaction and streamline trade.
```python
df["Processing_Days"] = (df["Receipt_date"] - df["Reg_date"]).dt.days
df["Processing_Days"].mean(), (df["Processing_Days"] > 7).mean() * 100
```
### 5. Compliance Gaps
On-time payment compliance stands at 80.1%, meaning nearly 20% of importers delayed tax payments beyond the due date.

This gap highlights areas where enforcement could be strengthened, such as implementing automated reminders, penalties, or real-time monitoring systems. Improving compliance can enhance revenue collection and reduce administrative burdens.
```python
df["On_Time"] = df["Receipt_date"] <= df["Due_date"]
df["On_Time"].mean()
```
### 6. Seasonal and Temporal Trends
rade volumes fluctuate significantly over the year. For instance, CIF imports peaked at approximately $355 billion in January 2022, before dropping to $96 billion in March 2022.

These fluctuations suggest predictable seasonal trade cycles driven by factors such as festive periods, agricultural production, or shifts in global demand.

Recognizing these trends allows customs authorities to better forecast workload, allocate resources, and plan inspections or audits in line with expected trade volumes.
```python
monthly_cif = df.groupby(df["Reg_date"].dt.to_period("M"))["CIF_value($)"].sum()
monthly_cif
```

## Recommendations

Based on the analysis of trade and customs data, the following strategic recommendations are proposed for managers, policymakers, and operational leaders to strengthen trade oversight, optimize revenue collection, and enhance operational efficiency:

1. **Diversify Trade Partnerships**  
   Heavy reliance on a small number of countries exposes revenue streams to geopolitical and economic risks. Managers should explore trade agreements or incentives with alternative markets and promote domestic production where feasible. By broadening the import base, authorities can reduce vulnerability, maintain stable revenue flows, and improve supply chain resilience.

2. **Review and Refine Taxation Policies** 
   Current taxation is largely value-based, which can overlook the risk or cost associated with shipment size or volume. Authorities should evaluate hybrid taxation models that consider container size, weight, or cargo type alongside value. Implementing such policies can ensure a fairer tax structure, close loopholes, and optimize revenue collection without overburdening compliant importers.

3. **Strengthen Compliance and Enforcement Mechanisms** 
   Compliance gaps exist with delayed payments and occasional misclassification of goods. Managers should implement automated systems for reminders, penalties, and progress tracking. Additionally, consider incentive programs such as fast-track clearance for consistently compliant importers. These measures encourage timely payments, reduce manual follow-up, and build a culture of accountability across importers and internal teams.

4. **Improve Operational Efficiency in Processing** 
   Delays in customs clearance impact trade speed and importer costs. Operational leaders should leverage historical processing data to identify bottlenecks, underperforming offices, or procedural inefficiencies. Investing in digital solutions, workflow optimization, and staff training can reduce turnaround times, streamline operations, and enhance customer satisfaction for importers and exporters alike.

5. **Utilize Predictive Analytics for Planning and Forecasting**  
   Seasonal and cyclical trade patterns offer opportunities for proactive planning. Managers should implement predictive models to anticipate trade spikes, staffing needs, inspection schedules, and revenue inflows. Using data-driven forecasts ensures resources are allocated efficiently, potential bottlenecks are addressed before they escalate, and decision-making becomes more proactive rather than reactive.

6. **Establish Strategic Monitoring and Reporting Dashboards**  
   To maintain continuous oversight, authorities should implement interactive dashboards that track high-value trade flows, compliance rates, and operational KPIs in real-time. Such tools empower managers to monitor trends, identify anomalies quickly, and make informed strategic decisions, ensuring trade operations are both transparent and accountable.


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
The analysis of trade and customs data offers valuable insights into import patterns, taxation efficiency, and compliance performance. Key findings show that trade is often concentrated among a few countries and product categories, which can create potential dependency risks. Strong correlations between trade values and tax collected confirm the importance of these metrics in monitoring trade performance, while seasonal and temporal trends reveal predictable fluctuations that can inform operational planning.

Variations in tax contributions across product categories and the presence of outlier transactions indicate opportunities to strengthen compliance, optimize revenue collection, and reduce leakages. These insights underscore the importance of a data-driven approach to customs management, enabling authorities and policymakers to make informed decisions, enhance operational efficiency, and support evidence-based trade and economic policies.

By applying these findings, customs authorities can improve trade monitoring, diversify risk, implement targeted interventions, and create a more resilient and efficient trade ecosystem.

## Contact

For questions, collaborations, or project discussions:

**Maureen Okoro**              
- 📨 [Email](mailto:okoromaureen590@gmail.com")
- 🌐 [GitHub](https://github.com/mauree155]
)
- 🔗 [LinkedIn](https://ng.linkedin.com/in/maureen-okoro-8a1972245)
