import pandas as pd

# ================= LOAD FILES =================

portal_stock = pd.read_excel(r"C:\Users\Ahsan\Downloads\R3P_Stock_Report_2025-12-31 1.xlsx")
portal_price = pd.read_excel(r"C:\Users\Ahsan\Downloads\R3P_Buy_Price_31-12-25 1.xlsx")

odoo_stock   = pd.read_excel(r"C:\Users\Ahsan\Downloads\Odoo Qty 31-12-25 1.xlsx")
odoo_price   = pd.read_excel(r"C:\Users\Ahsan\Downloads\Odoo Price 31-12-25 1.xlsx")

# ================= FIX COLUMN NAMES =================

for df in [portal_stock, odoo_stock, portal_price, odoo_price]:
    df.rename(columns={"Variant ID": "VariantID"}, inplace=True)

# ================= GRADE COLUMNS =================

grade_cols = [
    "Brand New",
    "OpenBox",
    "Quality Pre-Loved A+",
    "Quality Pre-Loved A",
    "Quality Pre-Loved A-",
    "Quality Pre-Loved B",
    "Refurbished"
]

# ================= MELT ALL FILES =================

def melt_df(df, value_name, keep_name=False):
    id_vars = ["VariantID"]
    if keep_name and "Variant Name" in df.columns:
        id_vars.append("Variant Name")

    melted = df.melt(
        id_vars=id_vars,
        value_vars=grade_cols,
        var_name="Grade",
        value_name=value_name
    )

    melted[value_name] = (
        pd.to_numeric(melted[value_name], errors="coerce")
        .fillna(0)
        .astype(int)
    )

    return melted

portal_stock_m = melt_df(portal_stock, "PortalQty", keep_name=True)
odoo_stock_m   = melt_df(odoo_stock, "OdooQty")

portal_price_m = melt_df(portal_price, "PortalPrice")
odoo_price_m   = melt_df(odoo_price, "OdooPrice")

# ================= MERGE STEP BY STEP =================

df = pd.merge(
    portal_stock_m,
    odoo_stock_m,
    on=["VariantID", "Grade"],
    how="outer"
)

df = pd.merge(
    df,
    portal_price_m,
    on=["VariantID", "Grade"],
    how="left"
)

df = pd.merge(
    df,
    odoo_price_m,
    on=["VariantID", "Grade"],
    how="left"
)

# ================= FILL MISSING =================

for col in ["PortalQty", "OdooQty", "PortalPrice", "OdooPrice"]:
    df[col] = df[col].fillna(0).astype(int)

# ================= FILTER: KEEP ONLY ROWS WHERE BOTH PORTAL AND ODOO QTY > 0 =================

df = df[(df["PortalQty"] > 0) & (df["OdooQty"] > 0) & (df["PortalPrice"] > 0) & (df["OdooPrice"] > 0)]

# ================= MATCH FLAGS =================

df["QtyMatch"]   = df["PortalQty"] == df["OdooQty"]
df["PriceMatch"] = df["PortalPrice"] == df["OdooPrice"]

# ================= REMARK LOGIC =================

def remark(row):
    """
    Determine a human-readable remark describing differences between portal and Odoo product data.
    Parameters
    ----------
    row : Mapping (e.g., dict or pandas.Series)
        Expected keys:
          - "PortalQty" (numeric): quantity reported by the portal
          - "PortalPrice" (numeric): price reported by the portal
          - "OdooQty" (numeric): quantity reported by Odoo
          - "OdooPrice" (numeric): price reported by Odoo
          - "QtyMatch" (bool): whether quantities match between portal and Odoo
          - "PriceMatch" (bool): whether prices match between portal and Odoo
    Returns
    -------
    str
        One of:
          - "Missing in Portal"         : portal has zero quantity and zero price, while Odoo shows a quantity or price (> 0)
          - "Quantity Missing in Odoo" : Odoo quantity is zero but portal quantity is > 0
          - "Price Missing in Odoo"    : Odoo price is zero but portal price is > 0
          - "Qty & Price Mismatch"     : neither quantity nor price match
          - "Qty Mismatch"             : quantity does not match
          - "Price Mismatch"           : price does not match
          - "OK"                       : no detected issues
    Behavior notes
    --------------
    - The function checks conditions in order and returns the first matching remark (priority matters).
    - The specific line:
          if row["PortalQty"] == 0 and row["PortalPrice"] == 0 and (row["OdooQty"] > 0 or row["OdooPrice"] > 0):
      detects items that are effectively missing from the portal (both portal quantity and portal price are zero)
      while Odoo indicates the item exists (either Odoo quantity > 0 or Odoo price > 0). When true, it returns
      "Missing in Portal".
    - Assumes numeric comparisons are valid; missing keys will raise KeyError and non-numeric types may raise TypeError.
    """
    
    if row["PortalQty"] == 0 and row["PortalPrice"] == 0 and (
        row["OdooQty"] > 0 or row["OdooPrice"] > 0
    ):
        return "Missing in Portal"

    if row["OdooQty"] == 0 and row["PortalQty"] > 0:
        return "Quantity Missing in Odoo"

    if row["OdooPrice"] == 0 and row["PortalPrice"] > 0 and row["PortalQty"] != row["OdooQty"]:
        return "Price Missing in Odoo and Qty Mismatch"
    
    if not row["QtyMatch"] and not row["PriceMatch"]:
        return "Qty & Price Mismatch"

    if not row["QtyMatch"]:
        return "Qty Mismatch"

    if not row["PriceMatch"]:
        return "Price Mismatch"

    return "OK"

df["Remark"] = df.apply(remark, axis=1)

# ================= FINAL OUTPUT =================

final = df[[
    "VariantID",
    "Variant Name",
    "Grade",
    "PortalQty",
    "OdooQty",
    "PortalPrice",
    "OdooPrice",
    "QtyMatch",
    "PriceMatch",
    "Remark"
]]

final.to_csv(r"E:\R3 Factory\Selenium_Prodcut_Scrapper\Scrapper_Results\Mapped_Result.csv", index=False)

print("DONE — Qty & Price mapping completed")
