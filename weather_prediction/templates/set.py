# ===============================
# 1️⃣ Install & import packages
# ===============================


import pandas as pd
import os
import kagglehub
from functools import reduce

# ===============================
# 2️⃣ Download dataset
# ===============================
path = kagglehub.dataset_download("pratikjadhav05/indian-weather-data")
print("Dataset path:", path)

# ===============================
# 3️⃣ Load all CSV / Excel files
# ===============================
def load_file(fp):
    if fp.endswith(".csv"):
        return pd.read_csv(fp)
    if fp.endswith((".xls", ".xlsx")):
        return pd.read_excel(fp)
    return None

dfs = []
for f in os.listdir(path):
    df = load_file(os.path.join(path, f))
    if df is not None:
        dfs.append(df)

# ===============================
# 4️⃣ Merge datasets
# ===============================
common_cols = set(dfs[0].columns)
for d in dfs[1:]:
    common_cols &= set(d.columns)

df = reduce(
    lambda a, b: pd.merge(a, b, on=list(common_cols), how="outer"),
    dfs
)

# ===============================
# 5️⃣ Extract required columns
# ===============================
location_df = df[[
    "location_name",
    "region",
    "latitude",
    "longitude"
]].dropna()

# Remove duplicates
location_df = location_df.drop_duplicates(
    subset=["location_name", "region"]
).reset_index(drop=True)

print("Total unique locations:", len(location_df))

# ===============================
# 6️⃣ Generate HTML blocks
# ===============================
html_blocks = []

for _, row in location_df.iterrows():
    html = f'''
<div class="map-label district"
     data-state="{row["region"]}"
     data-lat="{row["latitude"]}"
     data-lon="{row["longitude"]}">
  {row["location_name"]}
</div>
'''
    html_blocks.append(html)

# ===============================
# 7️⃣ Print sample output
# ===============================
print("SAMPLE OUTPUT:\n")
print("".join(html_blocks[:10]))

# ===============================
# 8️⃣ (Optional) Save to file
# ===============================
with open("district_map_label.html", "w", encoding="utf-8") as f:
    f.write("\n".join(html_blocks))

print("✅ HTML saved as district_map_labels.html")
