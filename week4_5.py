"""
Week 4-5 Deliverable

This script prepares the MLS datasets for analysis by:
1. Loading the Week 2-3 datasets.
2. Converting date and numeric fields.
3. Removing redundant columns.
4. Flagging and removing invalid records.
5. Performing date consistency checks.
6. Performing geographic data quality checks.
7. Saving cleaned datasets.
"""

import pandas as pd

#load datasets

sold = pd.read_csv("CombinedSoldResidentialRates.csv", low_memory=False)

listings = pd.read_csv("CombinedListingsResidentialRates.csv", low_memory=False)

print("Datasets loaded.\n")

print("Before Cleaning")
print(f"Sold Rows: {len(sold):,}")
print(f"Listings Rows: {len(listings):,}")

#convert data columns

date_columns = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate"
]


def convert_dates(df):

    for column in date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    return df


sold = convert_dates(sold)
listings = convert_dates(listings)

print("\nDate conversion complete.")

#convert numeric columns

numeric_columns = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
    "Latitude",
    "Longitude"
]


def convert_numeric(df):

    for column in numeric_columns:

        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


sold = convert_numeric(sold)
listings = convert_numeric(listings)

print("Numeric conversion complete.")

# remove duplicate ".1" columns

def remove_duplicate_columns(df):

    duplicate_columns = [
        column
        for column in df.columns
        if column.endswith(".1")
    ]

    df = df.drop(columns=duplicate_columns)

    return df


sold = remove_duplicate_columns(sold)
listings = remove_duplicate_columns(listings)

print("Duplicate columns removed.")

#flag invalid numeric columns

def create_invalid_flags(df, dataset):

    price_column = "ClosePrice" if dataset == "Sold" else "ListPrice"

    df["invalid_price_flag"] = df[price_column] <= 0
    df["invalid_area_flag"] = df["LivingArea"] <= 0

    if "DaysOnMarket" in df.columns:
        df["invalid_dom_flag"] = df["DaysOnMarket"] < 0

    df["invalid_bedroom_flag"] = df["BedroomsTotal"] < 0
    df["invalid_bathroom_flag"] = (
        df["BathroomsTotalInteger"] < 0
    )

    return df


sold = create_invalid_flags(sold, "Sold")
listings = create_invalid_flags(listings, "Listings")

#removing invalid records
sold_before = len(sold)
listing_before = len(listings)

sold = sold[
    (sold["ClosePrice"] > 0)
    &
    (sold["LivingArea"] > 0)
    &
    (sold["DaysOnMarket"] >= 0)
    &
    (sold["BedroomsTotal"] >= 0)
    &
    (sold["BathroomsTotalInteger"] >= 0)
]

listings = listings[
    (listings["ListPrice"] > 0)
    &
    (listings["LivingArea"] > 0)
    &
    (listings["BedroomsTotal"] >= 0)
    &
    (listings["BathroomsTotalInteger"] >= 0)
]

print("\nInvalid records removed.")

print(f"Sold removed: {sold_before - len(sold):,}")
print(f"Listings removed: {listing_before - len(listings):,}")


#date consistency checks
sold["listing_after_close_flag"] = (
    sold["ListingContractDate"] >
    sold["CloseDate"]
)

sold["purchase_after_close_flag"] = (
    sold["PurchaseContractDate"] >
    sold["CloseDate"]
)

sold["negative_timeline_flag"] = (
    sold["ListingContractDate"] >
    sold["PurchaseContractDate"]
)

print("\nDate Consistency Flags")

print(
    sold[
        [
            "listing_after_close_flag",
            "purchase_after_close_flag",
            "negative_timeline_flag"
        ]
    ].sum()
)

#geographic quality checks
def geographic_flags(df):

    df["missing_coordinates_flag"] = (
        df["Latitude"].isna()
        |
        df["Longitude"].isna()
    )

    df["zero_coordinates_flag"] = (
        (df["Latitude"] == 0)
        |
        (df["Longitude"] == 0)
    )

    df["positive_longitude_flag"] = (
        df["Longitude"] > 0
    )

    df["outside_california_flag"] = (
        (
            (df["Latitude"] < 32)
            |
            (df["Latitude"] > 42)
            |
            (df["Longitude"] < -124)
            |
            (df["Longitude"] > -114)
        )
        &
        ~df["missing_coordinates_flag"]
        &
        ~df["zero_coordinates_flag"]
    )

    return df


sold = geographic_flags(sold)
listings = geographic_flags(listings)

print("\nGeographic Quality Summary")

for label, df in [("Sold", sold), ("Listings", listings)]:

    print(f"\n{label}")

    print(
        "Missing coordinates:",
        df["missing_coordinates_flag"].sum()
    )

    print(
        "Zero coordinates:",
        df["zero_coordinates_flag"].sum()
    )

    print(
        "Positive longitude:",
        df["positive_longitude_flag"].sum()
    )

    print(
        "Outside California:",
        df["outside_california_flag"].sum()
    )


#summary after being cleaned 
print("\nAfter Cleaning")

print(f"Sold Rows: {len(sold):,}")
print(f"Listings Rows: {len(listings):,}")

print("\nData Types")

print(sold.dtypes)

#save cleaned datasets

sold.to_csv( "CombinedSoldResidentialCleaned.csv", index=False)

listings.to_csv("CombinedListingsResidentialCleaned.csv", index=False)

print("\nFinished!")

#created new files
print("Files Created:")
print("- CombinedSoldResidentialCleaned.csv")
print("- CombinedListingsResidentialCleaned.csv")