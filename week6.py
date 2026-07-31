"""
Week 6 Deliverable

1. Loads the cleaned residential datasets
2. Uses new market metrics
3. Creates time-series variables
4. Calculates transaction timeline metrics
5. Adds California school districts using latitude/longitude
6. Creates segmented market summaries
7. Saves engineered datasets for Tableau
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point 

# load cleaned datasets from previous weeks 
sold = pd.read_csv(
    "data/CombinedSoldResidentialCleaned.csv",
    low_memory=False
)

listings = pd.read_csv(
    "data/CombinedListingsResidentialCleaned.csv",
    low_memory=False
)

print(f"Sold Dataset Shape: {sold.shape}")
print(f"Listings Dataset Shape: {listings.shape}")

#convert date columns
date_columns = [
    "CloseDate",
    "ListingContractDate",
    "PurchaseContractDate"
]

for column in date_columns:

    if column in sold.columns:
        sold[column] = pd.to_datetime(
            sold[column],
            errors="coerce"
        )

    if column in listings.columns:
        listings[column] = pd.to_datetime(
            listings[column],
            errors="coerce"
        )

#feature engineering 
print("\nCreating engineered features...")

# Price Ratio
sold["PriceRatio"] = (
    sold["ClosePrice"] /
    sold["OriginalListPrice"]
)

# Close to Original List Ratio
sold["CloseToOriginalListRatio"] = (
    sold["ClosePrice"] /
    sold["OriginalListPrice"]
)

# Price Per Square Foot
sold["PricePerSqFt"] = (
    sold["ClosePrice"] /
    sold["LivingArea"]
)

# Keep Days On Market as engineered feature
sold["MarketDays"] = sold["DaysOnMarket"]


#time variables
sold["Year"] = sold["CloseDate"].dt.year

sold["Month"] = sold["CloseDate"].dt.month

sold["YrMo"] = (
    sold["CloseDate"]
        .dt
        .to_period("M")
        .astype(str)
)


#transaction timeline metrics
sold["ListingToContractDays"] = (
    sold["PurchaseContractDate"] -
    sold["ListingContractDate"]
).dt.days

sold["ContractToCloseDays"] = (
    sold["CloseDate"] -
    sold["PurchaseContractDate"]
).dt.days

print("Finished creating engineered columns.")

#add same features to the listings dataset
listings["PricePerSqFt"] = (
    listings["ListPrice"] /
    listings["LivingArea"]
)

listings["MarketDays"] = listings["DaysOnMarket"]

listings["Year"] = listings["ListingContractDate"].dt.year

listings["Month"] = listings["ListingContractDate"].dt.month

listings["YrMo"] = (
    listings["ListingContractDate"]
        .dt
        .to_period("M")
        .astype(str)
)

print("Listings features completed.")

#adding school district information
districts = gpd.read_file(
    "data/districts/DistrictAreas2425.shp"
)

# rename truncated shapefile columns
districts = districts.rename(columns={
    "DistrictNa": "DistrictName",
    "DistrictTy": "DistrictType"
})

# keeping only Unified School Districts
districts = districts[
    districts["DistrictType"] == "Unified"
].copy()

print(f"Loaded {len(districts)} Unified School District boundaries.")

#creating geodataframe for sold properties
print("Creating geographic points for sold properties...")

sold_geo = sold.dropna(
    subset=["Latitude", "Longitude"]
).copy()

sold_geo = gpd.GeoDataFrame(
    sold_geo,
    geometry=gpd.points_from_xy(
        sold_geo["Longitude"],
        sold_geo["Latitude"]
    ),
    crs="EPSG:4326"
)

#creating geodataframe for listings
print("Creating geographic points for listing properties...")

listings_geo = listings.dropna(
    subset=["Latitude", "Longitude"]
).copy()

listings_geo = gpd.GeoDataFrame(
    listings_geo,
    geometry=gpd.points_from_xy(
        listings_geo["Longitude"],
        listings_geo["Latitude"]
    ),
    crs="EPSG:4326"
)


#match coordinate systms
if districts.crs is None:
    print("District shapefile has no CRS. Setting CRS to EPSG:4326.")
    districts = districts.set_crs(epsg=4326)

# If the CRS differs, convert it.
if districts.crs != sold_geo.crs:
    districts = districts.to_crs(sold_geo.crs)


#spatial join
print("Assigning school districts...")

sold_join = gpd.sjoin(
    sold_geo,
    districts[["DistrictName", "DistrictType", "geometry"]],
    how="left",
    predicate="within"
)

listings_join = gpd.sjoin(
    listings_geo,
    districts[["DistrictName", "DistrictType", "geometry"]],
    how="left",
    predicate="within"
)

#copying school district back 
sold["SchoolDistrict"] = None
sold["DistrictType"] = None

sold.loc[
    sold_join.index,
    "SchoolDistrict"
] = sold_join["DistrictName"].values

sold.loc[
    sold_join.index,
    "DistrictType"
] = sold_join["DistrictType"].values

listings["SchoolDistrict"] = None
listings["DistrictTy"] = None

listings.loc[
    listings_join.index,
    "SchoolDistrict"
] = listings_join["DistrictName"].values

listings.loc[
    listings_join.index,
    "DistrictType"
] = listings_join["DistrictType"].values

print("\nSchool district assignment complete.")

print(
    sold[
        ["Latitude",
         "Longitude",
         "SchoolDistrict",
         "DistrictType"]
    ].head(10)
)

#sample output table
print("\nSample Engineered Features\n")

sample_columns = [
    "ClosePrice",
    "OriginalListPrice",
    "LivingArea",
    "PriceRatio",
    "CloseToOriginalListRatio",
    "PricePerSqFt",
    "MarketDays",
    "Year",
    "Month",
    "YrMo",
    "ListingToContractDays",
    "ContractToCloseDays",
    "SchoolDistrict",
    "DistrictType"
]

print(
    sold[sample_columns]
    .head(10)
)

#property type summary
print("\nProperty Type Summary")

property_summary = (
    sold
    .groupby("PropertyType")
    .agg(
        AverageClosePrice=("ClosePrice", "mean"),
        AveragePricePerSqFt=("PricePerSqFt", "mean"),
        AverageDaysOnMarket=("MarketDays", "mean"),
        Sales=("ClosePrice", "count")
    )
    .round(2)
)

print(property_summary)

property_summary.to_csv(
    "PropertyTypeSummary.csv"
)

#property subtype summary
print("\nProperty SubType Summary")

property_subtype_summary = (
    sold
    .groupby("PropertySubType")
    .agg(
        AverageClosePrice=("ClosePrice", "mean"),
        AveragePricePerSqFt=("PricePerSqFt", "mean"),
        AverageDaysOnMarket=("MarketDays", "mean"),
        Sales=("ClosePrice", "count")
    )
    .round(2)
)

print(property_subtype_summary.head(20))

property_subtype_summary.to_csv(
    "PropertySubTypeSummary.csv"
)

#county summary 
print("\nCounty Summary")

county_summary = (
    sold
    .groupby("CountyOrParish")
    .agg(
        AverageClosePrice=("ClosePrice", "mean"),
        AveragePricePerSqFt=("PricePerSqFt", "mean"),
        AverageDaysOnMarket=("MarketDays", "mean"),
        Sales=("ClosePrice", "count")
    )
    .round(2)
)

print(county_summary)

county_summary.to_csv(
    "CountySummary.csv"
)


#mls area summary 
print("\nMLS Area Summary")

mls_summary = (
    sold
    .groupby("MLSAreaMajor")
    .agg(
        AverageClosePrice=("ClosePrice", "mean"),
        AveragePricePerSqFt=("PricePerSqFt", "mean"),
        AverageDaysOnMarket=("MarketDays", "mean"),
        Sales=("ClosePrice", "count")
    )
    .round(2)
)

print(mls_summary.head(20))

mls_summary.to_csv(
    "MLSAreaSummary.csv"
)

#listing office summary
print("\nListing Office Summary")

listoffice_summary = (
    sold
    .groupby("ListOfficeName")
    .agg(
        AverageClosePrice=("ClosePrice", "mean"),
        AveragePricePerSqFt=("PricePerSqFt", "mean"),
        AverageDaysOnMarket=("MarketDays", "mean"),
        Sales=("ClosePrice", "count")
    )
    .round(2)
)

print(
    listoffice_summary
    .sort_values("Sales", ascending=False)
    .head(20)
)

listoffice_summary.to_csv(
    "ListOfficeSummary.csv"
)


#buyer office summary 
print("\nBuyer Office Summary")

buyeroffice_summary = (
    sold
    .groupby("BuyerOfficeName")
    .agg(
        AverageClosePrice=("ClosePrice", "mean"),
        AveragePricePerSqFt=("PricePerSqFt", "mean"),
        AverageDaysOnMarket=("MarketDays", "mean"),
        Sales=("ClosePrice", "count")
    )
    .round(2)
)

print(
    buyeroffice_summary
    .sort_values("Sales", ascending=False)
    .head(20)
)

buyeroffice_summary.to_csv(
    "BuyerOfficeSummary.csv"
)

#saving the summaries 
print("\nSaving engineered datasets...")

sold.to_csv(
    "CombinedSoldResidentialFeatures.csv",
    index=False
)

listings.to_csv(
    "CombinedListingsResidentialFeatures.csv",
    index=False
)

print("\nFinal Dataset Shapes")
print(f"Sold Dataset: {sold.shape}")
print(f"Listings Dataset: {listings.shape}")
