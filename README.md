# 🌀 Philippine Typhoon Analytics: End-to-End Data Pipeline (1951-2025)

## 📌 Project Overview
As an Electronics Engineering graduate, I developed this project to demonstrate the intersection of **Physical Data Science** and **Business Intelligence**. This repository contains a full-stack data pipeline that transforms 74 years of raw meteorological text records from the Japan Meteorological Agency (JMA) into an interactive Decision Support System for Philippine typhoon risk assessment.

## Screenshots

<img width="1919" height="1018" alt="Screenshot 2026-01-21 003029" src="https://github.com/user-attachments/assets/d88cef7a-e0eb-49dd-8590-49d705d148da" />
<img width="1917" height="1017" alt="image" src="https://github.com/user-attachments/assets/af4f88d6-cf7c-4013-ab17-bf2914a947ac" />
<img width="1917" height="957" alt="image" src="https://github.com/user-attachments/assets/134fd22e-c640-4ee2-a9d3-0ad1ae8b0db3" />
<img width="1301" height="663" alt="Screenshot 2026-01-20 230132" src="https://github.com/user-attachments/assets/2640617c-b184-4576-932a-7e08443ea2f7" />
<img width="683" height="632" alt="Screenshot 2026-01-20 180407" src="https://github.com/user-attachments/assets/3d110b69-6cf0-43fc-bf78-03d2cecebedd" />

---

## 🏗️ The Data Pipeline

### 1. Data Engineering & Extraction (Python)
The foundation of this project is a custom Python engine (`main.py`) designed to parse unstructured "Best Track" text files.
* **Regex Parsing:** Extracted storm headers and coordinate data from complex, non-standard JMA text formats.
* **Physics-Based Estimation:** For historical records missing wind speed, I implemented the **Atkinson & Holliday Wind-Pressure Relationship** formula to estimate intensity.
* **Geospatial Geofencing:** Built a "Point-in-Polygon" logic to categorize every coordinate as either **'Inside PAR'** (Philippine Area of Responsibility) or 'Outside PAR', creating a localized dataset.

### 2. Relational Database Analysis (SQL)
After cleaning the data, I utilized a MySQL environment to perform deep-dive time-series analytics.
* **Window Functions:** Used `LAG()` to detect **Rapid Intensification** (pressure drops of ≥24hPa within 24 hours).
* **Multi-Factor Ranking:** Developed an intensity ranking system using Wind Speed as the primary metric and Central Pressure as a secondary tie-breaker.
* **Decadal Binning:** Aggregated data by decade to visualize the frequency shift of Super Typhoons over the last 70 years.

### 3. Business Intelligence & Storytelling (Power BI)
* **Dynamic DAX Measures:** Created measures to instantly calculate Peak Wind and Lowest Pressure based on user-selected slicers.
* **Geospatial Tracking:** Visualized color-coded typhoon paths across the archipelago using Latitude/Longitude datasets.

---

## 🛠️ Challenges & Methodology (The "Engineering" Journey)

Building this project involved overcoming significant data quality hurdles typical of long-term environmental datasets:

### A. The Naming Discrepancy (JMA vs. PAGASA)
A major challenge was reconciling storm names. The JMA uses international names, while the Philippines (PAGASA) assigns local names. 
* **The Gap:** Systematic local naming in the Philippines only became consistent around **1963**. 
* **The Solution:** I cross-referenced international IDs with local lists to map names like *Haiyan* to *Yolanda*. For storms pre-1963, I maintained the international name or ID to preserve data integrity, ensuring that historical intensity trends weren't lost due to missing labels.

### B. Handling the "Silent Decade" (1970s–1980s Data Gaps)
While analyzing the dataset, I identified significant gaps in **Maximum Sustained Wind Speed** data during the 1970s and 1980s. 
* **The Issue:** Many early records only logged Central Pressure (hPa) but left Wind Speed (knots) blank.
* **The Engineering Fix:** Rather than deleting these rows, I applied the **Atkinson & Holliday formula**: 
  $$V = 6.7 \times (1010 - P)^{0.644}$$
  This allowed for a "filled" intensity record, enabling a fair comparison between the "Satellite Era" and the "Pre-Satellite Era."



### C. Deducing Storm Classifications
Since storm classifications (e.g., "Super Typhoon") changed over decades, I standardized the grading based on the current **PAGASA Category Scale**. This involved building a Python function to re-classify every single 6-hour data point based on its sustained wind speed, ensuring a 2025 standard was applied to a 1951 storm.

---

## 📈 Key Insights & The "Yolanda Paradox"

1.  **Intensity vs. Pressure:** Data shows that **Typhoon Yolanda (2013)** is not the #1 storm by *minimum pressure* (beaten by 1970s storms), but it remains the #1 most powerful by *wind speed* at landfall. This highlight's the importance of multi-factor sorting in engineering.
2.  **Rapid Intensification (RI):** My SQL analysis detected an increasing frequency of RI events in the last 15 years, where storms jump two categories higher in under 24 hours—a critical insight for disaster preparedness.
3.  **Seasonality:** While August has the *most* storms, the *strongest* storms (highest average wind speeds) statistically enter the PAR during **October and November**.

---

## 🛠️ Technical Stack
* **Languages:** Python (Pandas, NumPy, Regex), SQL (MySQL)
* **Visualization:** Power BI (DAX, Power Query)
* **Concepts:** Geospatial Analysis, ETL Pipelines, Mathematical Modeling, Time-Series Forecasting.

---

## 👨‍💻 About the Author
**Val Rique Tajaros** | *Electronics Engineering Graduate*
Passionate about transforming raw sensor and environmental data into actionable insights through Data Engineering and Analytics.
