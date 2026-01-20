# 🌀 Philippine Typhoon Analytics: End-to-End Data Pipeline (1951-2025)

## 📌 Project Overview
As an Electronics Engineering graduate, I developed this project to demonstrate the intersection of **Physical Data Science** and **Business Intelligence**. This repository contains a full-stack data pipeline that transforms raw meteorological text records from the Japan Meteorological Agency (JMA) into an interactive Decision Support System for Philippine typhoon risk assessment.

---

## Screenshots

<img width="1919" height="1018" alt="Screenshot 2026-01-21 003029" src="https://github.com/user-attachments/assets/d88cef7a-e0eb-49dd-8590-49d705d148da" />
<img width="1917" height="1017" alt="image" src="https://github.com/user-attachments/assets/af4f88d6-cf7c-4013-ab17-bf2914a947ac" />
<img width="1917" height="957" alt="image" src="https://github.com/user-attachments/assets/134fd22e-c640-4ee2-a9d3-0ad1ae8b0db3" />
<img width="1301" height="663" alt="Screenshot 2026-01-20 230132" src="https://github.com/user-attachments/assets/2640617c-b184-4576-932a-7e08443ea2f7" />
<img width="683" height="632" alt="Screenshot 2026-01-20 180407" src="https://github.com/user-attachments/assets/3d110b69-6cf0-43fc-bf78-03d2cecebedd" />

## 🏗️ The Data Pipeline

### 1. Data Engineering & Extraction (Python)
The foundation of this project is a custom Python engine (`main.py`) designed to parse "Best Track" text files.
* **Regex Parsing:** Extracted storm headers and coordinate data from complex, non-standard JMA text formats.
* **Physics-Based Estimation:** For historical records missing wind speed, I implemented the **Atkinson & Holliday Wind-Pressure Relationship** formula to estimate intensity.
* **Geospatial Geofencing:** Built a "Point-in-Polygon" logic to categorize every coordinate as either **'Inside PAR'** (Philippine Area of Responsibility) or 'Outside PAR', creating a localized dataset for the Philippines.

### 2. Relational Database Analysis (SQL)
After cleaning the data into `ph_typhoon_data_v4.csv`, I imported it into a MySQL environment to perform deep-dive analytics.
* **Window Functions:** Used `LAG()` to detect **Rapid Intensification** (pressure drops of 24hPa within 24 hours).
* **Multi-Factor Ranking:** Developed a ranking system for "Destructiveness" by sorting through Max Wind Speeds and using Central Pressure as a secondary tie-breaker.
* **Climate Trends:** Aggregated data by decade to visualize the frequency shift of Super Typhoons over the last 70 years.

### 3. Business Intelligence & Storytelling (Power BI)
The final output is an interactive dashboard designed for disaster risk researchers.
* **Dynamic DAX Measures:** Created measures to instantly calculate Peak Wind and Lowest Pressure based on user-selected slicers.
* **Geospatial Tracking:** Visualized typhoon paths across the archipelago, color-coded by storm classification.
* **Interactive Slicers:** Allows users to search for specific historical storms (e.g., Yolanda, Odette, Juan) to see localized impact metrics.

---

## 🛠️ Technical Stack
* **Languages:** Python (Pandas, NumPy, Regex), SQL (MySQL)
* **Visualization:** Power BI (DAX, Power Query)
* **Engineering Concepts:** Geospatial Analysis, Time-Series Data Wrangling, Mathematical Modeling.

---

## 📈 Key Insights
* **The Yolanda Paradox:** Data shows that while Typhoon Yolanda (2013) is not the #1 most "intense" storm by pressure, it remains the #1 most "destructive" by wind speed at landfall.
* **Seasonality:** While the most storms occur in August, the highest average wind speeds for systems inside the PAR occur in **October and November**.

---

## 📂 Repository Structure
* `scripts/`: Python data engineering scripts.
* `sql/`: SQL analysis queries and technical documentation.
* `data/`: The final cleaned dataset (CSV).
* `dashboard/`: Power BI `.pbix` file.

---

## 👨‍💻 About the Author
**Val Rique Tajaros** Passionate about transforming raw sensor and environmental data into actionable insights through Data Engineering and Analytics.
