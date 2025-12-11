import pandas as pd

# Load datasets
portal = pd.read_excel(r"C:\Users\Ahsan\Downloads\R3 Production Qty.xlsx")
odoo = pd.read_excel(r"C:\Users\Ahsan\Downloads\Odoo Retail Stock.xlsx")

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
    value_name="OdooQty"
)

# Keep only rows where OdooQty is not empty
odoo_melted["OdooQty"] = odoo_melted["OdooQty"].fillna(0).astype(int)
odoo_melted = odoo_melted[odoo_melted["OdooQty"] > 0]

# ---- MELT PORTAL TOO ----
portal_melted = portal.melt(
    id_vars=["VariantID", "Variant Name"],
    value_vars=grade_cols,
    var_name="Grade",
    value_name="PortalQty"
)

portal_melted["PortalQty"] = portal_melted["PortalQty"].fillna(0).astype(int)

# ---- MERGE BOTH ----
df = pd.merge(
    portal_melted,
    odoo_melted,
    on=["VariantID", "Grade"],
    how="outer"
)

# Fill missing quantities
df["PortalQty"] = df["PortalQty"].fillna(0).astype(int)
df["OdooQty"] = df["OdooQty"].fillna(0).astype(int)

# ---- MATCH COLUMN ----
df["QtyMatch"] = df["PortalQty"] == df["OdooQty"]

# ---- REMARK ----
def remark(row):
    if row["PortalQty"] == 0 and row["OdooQty"] > 0:
        return "Missing in Portal"
    if row["PortalQty"] > 0 and row["OdooQty"] == 0:
        return "Missing in Odoo"
    if row["PortalQty"] != row["OdooQty"]:
        return "Quantity Mismatch"
    return "OK"

df["Remark"] = df.apply(remark, axis=1)

# ---- FINAL OUTPUT ----
final = df[[
    "VariantID",
    "Variant Name",
    "Grade",
    "PortalQty",
    "OdooQty",
    "QtyMatch",
    "Remark"
]]

final.to_csv("Mapped_Result.csv", index=False)
print("DONE — Mapped_Result.csv generated")
