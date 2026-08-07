"""
Week 7 Deliverable

1. Loads the engineered datasets
2. Detects outliers using the IQR method
3. Adds outlier flag columns
4. Creates filtered analysis datasets
5. Compares statistics before and after filtering
6. Saves flagged and filtered datasets
"""

import pandas as pd

# loading engineered datasets from last week 
sold = pd.read_csv(
    "CombinedSoldResidentialFeatures.csv",
    low_memory=False
)

listings = pd.read_csv(
    "CombinedListingsResidentialFeatures.csv",
    low_memory=False
)

print("Datasets loaded.\n")

print("Sold:", sold.shape)
print("Listings:", listings.shape)

iqr_columns = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket"
]

def add_iqr_flags(df, columns):
    df = df.copy()
    for column in columns:
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df[f"{column}_OutlierFlag"] = (
            (df[column] < lower_bound) |
            (df[column] > upper_bound)
        )

        print(f"\n{column}")
        print(f"Lower Bound: {lower_bound:.2f}")
        print(f"Upper Bound: {upper_bound:.2f}")
        print(
            "Outliers:",
            df[f"{column}_OutlierFlag"].sum()
        )
    return df 


sold = add_iqr_flags(sold, iqr_columns)

listings = add_iqr_flags(
    listings,
    ["LivingArea", "DaysOnMarket"] #no closeprice
)

#filtering
sold_filtered = sold[
    ~(
    sold["ClosePrice_OutlierFlag"] |
    sold["LivingArea_OutlierFlag"] |
    sold["DaysOnMarket_OutlierFlag"]
    )
].copy()

listings_filtered = listings[
    ~(
    listings["LivingArea_OutlierFlag"] |
    listings["DaysOnMarket_OutlierFlag"]
    )
].copy()

#comparison table 
comparison = pd.DataFrame({

    "Metric":[
        "Rows",
        "Median ClosePrice",
        "Median LivingArea",
        "Median DaysOnMarket"
    ],

    "Before":[
        len(sold),
        sold["ClosePrice"].median(),
        sold["LivingArea"].median(),
        sold["DaysOnMarket"].median()
    ],

    "After":[
        len(sold_filtered),
        sold_filtered["ClosePrice"].median(),
        sold_filtered["LivingArea"].median(),
        sold_filtered["DaysOnMarket"].median()
    ]

})

print("\nComparison")
print(comparison)

comparison.to_csv("Week7_Comparison.csv", index=False)

#saving both datasets 
sold.to_csv(
    "CombinedSoldResidentialOutlierFlags.csv",
    index=False
)

listings.to_csv(
    "CombinedListingsResidentialOutlierFlags.csv",
    index=False
)

#filtered versions
sold_filtered.to_csv(
    "CombinedSoldResidentialFiltered.csv",
    index=False
)

listings_filtered.to_csv(
    "CombinedListingsResidentialFiltered.csv",
    index=False
)





