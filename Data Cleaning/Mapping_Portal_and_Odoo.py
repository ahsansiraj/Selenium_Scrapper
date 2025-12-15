import pandas as pd

# Load datasets
portal = pd.read_excel(r"C:\Users\Ahsan\Downloads\Buy_Price_Portal.xlsx")
odoo = pd.read_excel(r"C:\Users\Ahsan\Downloads\Odoo Price 15-12-25 1.xlsx")

# ---- FIX PORTAL COLUMNS ----
portal.rename(columns={"Variant ID": "VariantID"}, inplace=True)

# Portal grade columns
grade_cols = [
    "Brand New",
    "OpenBox",
    "Quality Pre-Loved A+",
    "Quality Pre-Loved A",
    "Quality Pre-Loved A-",
    "Quality Pre-Loved B",
    "Refurbished"
]

# ---- FIX ODOO COLUMNS ----
odoo.rename(columns={"Variant ID": "VariantID"}, inplace=True)

# List all grade columns in Odoo except VariantID
odoo_grade_cols = [col for col in odoo.columns if col != "VariantID"]

# ---- MELT ODOO (convert columns → rows) ----
odoo_melted = odoo.melt(
    id_vars=["VariantID"],
    value_vars=odoo_grade_cols,
    var_name="Grade",
    value_name="OdooPrice"
)

# Keep only rows where OdooPrice is not empty
odoo_melted["OdooPrice"] = pd.to_numeric(odoo_melted["OdooPrice"], errors='coerce').fillna(0).astype(int)
odoo_melted = odoo_melted[odoo_melted["OdooPrice"] > 0]

# ---- MELT PORTAL TOO ----
portal_melted = portal.melt(
    id_vars=["VariantID", "Variant Name"],
    value_vars=grade_cols,
    var_name="Grade",
    value_name="PortalPrice"
)

# Convert all non-numeric values (including "Not Set") to NaN,
# Fill NaN with 0,
portal_melted["PortalPrice"] = (
    pd.to_numeric(portal_melted["PortalPrice"], errors='coerce')
    .fillna(0)
    .astype(int)
)

# ---- MERGE BOTH ----
df = pd.merge(
    portal_melted,
    odoo_melted,
    on=["VariantID", "Grade"],
    how="outer"
)

# Fill missing quantities
df["PortalPrice"] = df["PortalPrice"].fillna(0).astype(int)
df["OdooPrice"] = df["OdooPrice"].fillna(0).astype(int)

# ---- MATCH COLUMN ----
df["PriceMatch"] = df["PortalPrice"] == df["OdooPrice"]

# ---- REMARK ----
def remark(row):
    if row["PortalPrice"] == 0 and row["OdooPrice"] > 0:
        return "Missing in Portal"
    if row["PortalPrice"] > 0 and row["OdooPrice"] == 0:
        return "Missing in Odoo"
    if row["PortalPrice"] != row["OdooPrice"]:
        return "Price Mismatch"
    return "OK"

df["Remark"] = df.apply(remark, axis=1)

# ---- FINAL OUTPUT ----
final = df[[
    "VariantID",
    "Variant Name",
    "Grade",
    "PortalPrice",
    "OdooPrice",
    "PriceMatch",
    "Remark"
]]

final.to_csv("Mapped_Result.csv", index=False)
print("DONE — Mapped_Result.csv generated")
