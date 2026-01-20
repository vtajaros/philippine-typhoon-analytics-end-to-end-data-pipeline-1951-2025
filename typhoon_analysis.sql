/*
================================================================================
PROJECT: JMA-PAGASA Historical Typhoon Analytics (1951 - 2025)
AUTHOR: Val Rique Tajaros
ENGINEERING FOCUS: Geospatial Geofencing & Intensity Estimation Logic
================================================================================

TECHNICAL OVERVIEW:
This SQL suite analyzes tropical cyclone data enriched via Python. 
Key engineering and data science implementations include:

1. DATA CLEANING & TYPE CASTING:
   - Handled mismatched data types by casting Wind Speed and Pressure from strings 
     to DECIMALS for accurate numerical ranking (correcting '95 > 125' string errors).

2. METEOROLOGICAL TIE-BREAKING:
   - Implemented multi-factor sorting using Wind Speed (Velocity) as Primary and 
     Central Pressure (Barometric) as Secondary metrics to rank storm intensity.

3. ADVANCED TIME-SERIES ANALYTICS:
   - CTEs & Window Functions: Used LAG() over 24-hour partitions to identify 
     "Rapid Intensification" events (Pressure drop >= 24hPa in 24 hours).
   - Decadal Binning: Analyzed historical frequency shifts by grouping data into 
     10-year intervals using distinct StormID counting to avoid row-duplication bias.

4. GEOSPATIAL VALIDATION:
   - Queries focused on the "Inside PAR" flag, generated via a custom point-in-polygon 
     algorithm in Python to isolate impact on the Philippine archipelago.
================================================================================
*/

-- "How likely is a Super Typhoon to enter the Philippines compared to a weak Tropical Depression?"
SELECT 
    Classification,
    COUNT(DISTINCT StormID) as Total_Storms,
    COUNT(DISTINCT CASE WHEN In_PAR = 'Inside PAR' THEN StormID END) as Storms_Inside_PAR,
    ROUND((COUNT(DISTINCT CASE WHEN In_PAR = 'Inside PAR' THEN StormID END) / COUNT(DISTINCT StormID)) * 100, 2) as Hit_Rate_Percentage
FROM ph_typhoon_data_v4
GROUP BY Classification
ORDER BY Total_Storms DESC;


-- Which month brings the most intense winds to the Philippines?
SELECT 
    SUBSTRING(Timestamp, 5, 2) as Month,
    COUNT(DISTINCT StormID) as Storm_Count,
    ROUND(AVG(WindSpeed_kt), 1) as Avg_Wind_Speed
FROM ph_typhoon_data_v4
WHERE In_PAR = 'Inside PAR' AND WindSpeed_kt IS NOT NULL
GROUP BY Month
ORDER BY Avg_Wind_Speed DESC;

-- Top 20 Most Intense Storms (Inside PAR)
SELECT 
    Year,
    StormName,
    PAGASA_Name,
    MIN(Pressure_hPa) AS Lowest_Pressure,
    MAX(WindSpeed_kt) AS Max_Wind_Speed
FROM ph_typhoon_data_v4
WHERE In_PAR = 'Inside PAR'
GROUP BY StormID, Year, StormName, PAGASA_Name
ORDER BY Lowest_Pressure ASC
LIMIT 20;

/* "What were the 10 most powerful typhoons to ever enter the Philippine Area of 
Responsibility (PAR), based on their maximum sustained wind speeds?" */
SELECT 
    Year,
    StormName,
    PAGASA_Name,
    MAX(CAST(WindSpeed_kt AS DECIMAL(10,2))) AS Max_Wind,
    MIN(CAST(Pressure_hPa AS DECIMAL(10,2))) AS Min_Pressure
FROM ph_typhoon_data_v4
WHERE In_PAR = 'Inside PAR'
GROUP BY StormID, Year, StormName, PAGASA_Name
ORDER BY Max_Wind DESC, Min_Pressure ASC
LIMIT 10;


-- Show the full lifecycle of Yolanda from the moment it entered to the moment it exited PAR.
SELECT Timestamp, Latitude, Longitude, WindSpeed_kt, Pressure_hPa, Classification
FROM ph_typhoon_data_v4
WHERE StormName = 'HAIYAN' AND Year = 2013 AND In_PAR = 'Inside PAR'
ORDER BY Timestamp ASC;

-- Identify storms that underwent Rapid Intensification (24hPa drop in 24 hours)
WITH PressureDiff AS (
    SELECT 
        StormName,
        PAGASA_Name,
        Timestamp,
        Pressure_hPa,
        LAG(Pressure_hPa, 4) OVER (PARTITION BY StormID ORDER BY Timestamp) AS Pressure_24h_Ago
    FROM ph_typhoon_data_v4
)
SELECT 
    StormName, 
    PAGASA_Name, 
    Timestamp, 
    (Pressure_24h_Ago - Pressure_hPa) AS Intensity_Surge
FROM PressureDiff
WHERE (Pressure_24h_Ago - Pressure_hPa) >= 24
ORDER BY Intensity_Surge DESC;

-- Analyze the frequency of Super Typhoons by Decade (Corrected for Distinct IDs)
SELECT 
    CONCAT(FLOOR(Year / 10) * 10, 's') AS Decade,
    COUNT(DISTINCT StormID) AS Total_Unique_Storms,
    -- Count only unique StormIDs that reached Super Typhoon status in that decade
    COUNT(DISTINCT CASE WHEN Classification = 'Super Typhoon' THEN StormID END) AS Super_Typhoon_Count,
    -- Calculate percentage correctly
    ROUND(
        COUNT(DISTINCT CASE WHEN Classification = 'Super Typhoon' THEN StormID END) * 100.0 / 
        COUNT(DISTINCT StormID), 
    2) AS Percent_Super_Typhoons
FROM ph_typhoon_data_v4
WHERE In_PAR = 'Inside PAR'
GROUP BY Decade
ORDER BY Decade ASC;

-- Find which storms stayed inside the PAR the longest (Duration in Hours)
SELECT 
    StormName,
    PAGASA_Name,
    Year,
    COUNT(*) * 6 AS Hours_Inside_PAR
FROM ph_typhoon_data_v4
WHERE In_PAR = 'Inside PAR'
GROUP BY StormID, StormName, PAGASA_Name, Year
ORDER BY Hours_Inside_PAR DESC
LIMIT 10;


