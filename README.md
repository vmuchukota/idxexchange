# IDX Exchange · California Residential Market Analysis

**Vaishnavi Muchukota · Data Analyst Intern · Summer 2026**

I built a Python workflow to turn monthly California Regional MLS (CRMLS) listing and sales exports provided by IDX Exchange into analysis-ready datasets. I used Tableau to explore how residential prices, time on market, and sales activity varied over time, across local markets, and by property subtype.

## Tableau dashboards

| Dashboard | What it shows |
| --- | --- |
| California Residential Market Trends | Monthly median closing price, average days on market, and the average ratio of closing price to original asking price. |
| Market Activity & Property Insights | Monthly closed sales and new listings, plus median price per square foot by property subtype. Filters let readers compare counties, cities, ZIP codes, and property subtypes. |
| Top 100 Listing Agents & Offices | Listing agent and office rankings by sales volume, with transaction counts and geographic and property-subtype filters. |

## Analysis workflow

| Script | Contribution |
| --- | --- |
| [`week1.py`](week1.py) | Combined monthly CRMLS exports into separate residential sales and listings datasets and logged row counts before and after filtering. |
| [`week2_3.py`](week2_3.py) | Profiled missingness and numeric distributions, removed fields above 90% missingness, and joined monthly averages of [Freddie Mac’s 30-year fixed mortgage rate from FRED](https://fred.stlouisfed.org/series/MORTGAGE30US). Sales were matched by closing month and listings by listing contract month. |
| [`week4_5.py`](week4_5.py) | Standardized date and numeric fields, removed duplicate columns, screened out invalid price and property records, and flagged inconsistent dates and suspect coordinates. |
| [`week6.py`](week6.py) | Calculated price per square foot, sale-to-original-list price ratios, and transaction timelines. Used a point-in-polygon spatial join to assign properties to California unified school districts and produced market summaries by geography, property subtype, and brokerage office. |
| [`week7.py`](week7.py) | Applied the 1.5× interquartile range rule to flag outliers, saved flagged and filtered datasets, and compared how filtering changed sales row counts and median values. |

## Data and dependencies

The scripts use Python, pandas, Matplotlib, GeoPandas, and Shapely. The analysis uses CRMLS listing and sales exports, the public FRED mortgage-rate series, and California unified school district boundaries.

To run the scripts, use the order above and supply authorized CRMLS CSV exports named `CRMLSSoldYYYYMM.csv` and `CRMLSListingYYYYMM.csv` under `data/`. After Weeks 4–5, place both cleaned CSVs in `data/` for Week 6 and supply the district shapefile and its companion files under `data/districts/` as `DistrictAreas2425.*`. Run Week 7 from the same directory where Week 6 writes the engineered CSVs.
