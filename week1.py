import datetime
import pandas as pd
from pathlib import Path

#months to load 
today = datetime.date.today()

# last completed month
last_day_prev_month = today.replace(day=1) - datetime.timedelta(days=1)

months = (
    pd.date_range(
        start="2024-01",
        end=last_day_prev_month,
        freq="MS"
    )
    .strftime("%Y%m")
)


sold_dfs = []
sold_rows_before = 0

for month in months:
    filename = Path(f"data/CRMLSSold{month}.csv")
    if filename.exists():
        df = pd.read_csv(filename)
        sold_rows_before += len(df)
        sold_dfs.append(df)
        print(f"Loaded {filename.name} ({len(df):,} rows)")

    else:
        print(f"Missing {filename.name}")

sold = pd.concat(sold_dfs, ignore_index=True)

print("\n----- SOLD DATA -----")
print(f"Rows before concatenation: {sold_rows_before:,}")
print(f"Rows after concatenation : {len(sold):,}")

print(f"Rows before Residential filter: {len(sold):,}")
sold = sold[sold["PropertyType"] == "Residential"]
print(f"Rows after Residential filter : {len(sold):,}")

sold.to_csv(
    "CombinedSoldResidential.csv",
    index=False
)

# listing files

listing_dfs = []
listing_rows_before = 0
for month in months:
    filename = Path(f"data/CRMLSListing{month}.csv")
    if filename.exists():
        df = pd.read_csv(filename)
        listing_rows_before += len(df)
        listing_dfs.append(df)
        print(f"Loaded {filename.name} ({len(df):,} rows)")

    else:
        print(f"Missing {filename.name}")

# Concatenate

listings = pd.concat(listing_dfs, ignore_index=True)

print("\n----- LISTING DATA -----")
print(f"Rows before concatenation: {listing_rows_before:,}")
print(f"Rows after concatenation : {len(listings):,}")
print(f"Rows before Residential filter: {len(listings):,}")

listings = listings[
    listings["PropertyType"] == "Residential"
]

print(f"Rows after Residential filter : {len(listings):,}")
# Save

listings.to_csv(
    "CombinedListingsResidential.csv",
    index=False
)