"""
Week 2 and 3 Deliverable
This script does the following: 
1. Loads the combined residential datasets.
2. Inspects dataset structure. 
3. Creates a missing value report. 
4. Creates numeric distribution summaries. 
5. Merges monthly mortgage rates from FRED.
"""

import pandas as pd

# loading the combined residential datasets 
sold = pd.read_csv(
    "CombinedSoldResidential.csv",
    low_memory=False
)

listings = pd.read_csv(
    "CombinedListingsResidential.csv",
    low_memory=False
)

print("Datasets have been loaded successfully.\n")

#dataset inspection 

def inspect_dataset(df, name):

    print("=" * 60)
    print(name)
    print("=" * 60)

    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

    print("\nProperty Types:")
    print(df["PropertyType"].unique())

    print("\n")

inspect_dataset(sold, "Sold Dataset")
inspect_dataset(listings, "Listings Dataset")

#missing value report 
def missing_value_report(df, dataset_name):
    report = pd.DataFrame({
        "Column": df.columns, 
        "Missing Count": df.isnull().sum().values,
        "Percent Missing": (df.isnull().mean() * 100).round(2).values
    })

    report["Over 90% Missing"] = (report["Percent Missing"] > 90)

    filename = f"{dataset_name}_MissingReport.csv"

    report.to_csv(filename, index=False)

    print(f"{filename} saved.")

    return report

sold_missing = missing_value_report(sold, "Sold")
listing_missing = missing_value_report(listings, "Listings")


# numeric distribution summary

numeric_columns = [
    "ClosePrice",
    "LivingArea", 
    "DaysOnMarket"
]

def numeric_summary(df, dataset_name):
    summary = (
        df[numeric_columns]
        .describe(percentiles=[0.25, 0.5, 0.75])
        .T
    )

    summary.to_csv(f"{dataset_name}_NumericSummary.csv")

    print(f"{dataset_name}_NumericSummary.csv saved.")

    return summary

numeric_summary(sold, "Sold")
numeric_summary(listings, "Listings")

# download mortage rates from FRED
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"

# Read the CSV first
mortgage = pd.read_csv(url)

# convert the date column
mortgage["observation_date"] = pd.to_datetime(mortgage["observation_date"])

# rename for consistency
mortgage.rename(
    columns={
        "observation_date": "date",
        "MORTGAGE30US": "rate_30yr_fixed"
    },
    inplace=True
)

mortgage["year_month"] = (mortgage["date"].dt.to_period("M"))

mortgage_monthly = (
    mortgage.groupby("year_month")["rate_30yr_fixed"]
    .mean()
    .reset_index()
)

print("\nMortgage rate data downloaded.\n")

#creating join keys

sold["year_month"] = (pd.to_datetime(sold["CloseDate"]).dt.to_period("M"))

listings["year_month"] = (pd.to_datetime(listings["ListingContractDate"]).dt.to_period("M"))

#merge mortgage rates
sold = sold.merge(
    mortgage_monthly,
    on="year_month",
    how="left"
)

listings = listings.merge(
    mortgage_monthly,
    on="year_month",
    how="left"
)

#validate merge
print("Mortgage Rate Merge Validation")

print(
    "Sold missing mortgage rates:",
    sold["rate_30yr_fixed"].isnull().sum()
)

print(
    "Listings missing mortgage rates:",
    listings["rate_30yr_fixed"].isnull().sum()
)

#save the merged datasets
sold.to_csv(
    "CombinedSoldResidentialRates.csv",
    index=False
)

listings.to_csv(
    "CombinedListingsResidentialRates.csv",
    index=False
)

print("\nFinished!")

print("Files Created:")
print("- Sold_MissingReport.csv")
print("- Listings_MissingReport.csv")
print("- Sold_NumericSummary.csv")
print("- Listings_NumericSummary.csv")
print("- CombinedSoldResidentialRates.csv")
print("- CombinedListingsResidentialRates.csv")






