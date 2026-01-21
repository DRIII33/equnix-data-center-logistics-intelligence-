#INSTALL PACKAGES
!pip install pandas numpy


import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)

# --- SKU and Bins Generation ---
DATA_CENTERS = ["MI1", "SV1", "DA1"]
HAZARD_CLASSES = ["NONE", "LITHIUM_ION", "FLAMMABLE", "CORROSIVE"]
VENDORS = ["OEM_A", "OEM_B", "OEM_C"]

def generate_skus(n=50):
    return pd.DataFrame({
        "sku_id": [f"SKU-{i:04d}" for i in range(1, n+1)],
        "description": np.random.choice(
            ["Server Rail", "Fiber Cable", "SFP Module", "Power Supply"], n
        ),
        "hazard_class": np.random.choice(HAZARD_CLASSES, n, p=[0.7, 0.15, 0.1, 0.05]),
        "min_stock": np.random.randint(5, 20, n),
        "max_stock": np.random.randint(30, 100, n)
    })

def generate_bins():
    return pd.DataFrame({
        "bin_id": [f"BIN-{i:03d}" for i in range(1, 101)],
        "data_center": np.random.choice(DATA_CENTERS, 100)
    })

skus_df = generate_skus()
bins_df = generate_bins()

skus_df.to_csv("skus.csv", index=False)
bins_df.to_csv("bins.csv", index=False)

if os.path.exists('skus.csv') and os.path.exists('bins.csv'):
    print("skus.csv and bins.csv were successfully created.")
else:
    print("Error: One or both files were not created.")

# --- Shipments Generation ---
def generate_shipments(skus_list, n=1000):
    base_date = datetime.today() - timedelta(days=120)
    records = []

    for i in range(n):
        ship_date = base_date + timedelta(days=int(np.random.randint(0, 120)))
        expected = ship_date + timedelta(days=int(np.random.randint(1, 7)))
        actual_delay = int(np.random.choice([0, 0, 1, 3, 7, 15]))
        actual = expected + timedelta(days=actual_delay)

        records.append({
            "shipment_id": f"SHP-{i:06d}",
            "sku_id": np.random.choice(skus_list),
            "quantity": np.random.randint(1, 20),
            "ship_date": ship_date.date(),
            "expected_delivery": expected.date(),
            "actual_delivery": actual.date(),
            "direction": np.random.choice(["INBOUND", "OUTBOUND"])
        })

    return pd.DataFrame(records)

sku_ids_list = pd.read_csv("skus.csv")["sku_id"].tolist()
shipments_df = generate_shipments(sku_ids_list)
shipments_df.to_csv("shipments.csv", index=False)

if os.path.exists('shipments.csv'):
    print("shipments.csv was successfully created.")
else:
    print("Error: shipments.csv was not created.")

# --- Inventory Movements Generation ---
def generate_movements(skus_list, bins_list, n=5000):
    records = []
    base_date = datetime.today() - timedelta(days=120)

    for i in range(n):
        records.append({
            "movement_id": f"MOV-{i:07d}",
            "sku_id": np.random.choice(skus_list),
            "bin_id": np.random.choice(bins_list),
            "movement_type": np.random.choice(
                ["RECEIPT", "PICK", "TRANSFER", "ADJUSTMENT"],
                p=[0.35, 0.4, 0.15, 0.1]
            ),
            "quantity": np.random.randint(1, 10),
            "movement_date": (base_date + timedelta(days=np.random.randint(0, 120))).date()
        })

    return pd.DataFrame(records)

skus_list_for_movements = pd.read_csv("skus.csv")["sku_id"].tolist()
bins_list_for_movements = pd.read_csv("bins.csv")["bin_id"].tolist()

movements_df = generate_movements(skus_list_for_movements, bins_list_for_movements)
movements_df.to_csv("inventory_movements.csv", index=False)

if os.path.exists('inventory_movements.csv'):
    print("inventory_movements.csv was successfully created.")
else:
    print("Error: inventory_movements.csv was not created.")

# --- Physical Counts Generation ---
COUNT_TYPES = ["CYCLE_COUNT", "FULL_COUNT"]

def generate_physical_counts(skus_list, bins_list, start_date, months=4):
    records = []
    current_date = start_date

    for month in range(months):
        count_date = current_date + timedelta(days=30 * month)

        for sku in skus_list:
            for bin_id in np.random.choice(bins_list, size=np.random.randint(1, 4), replace=False):
                system_qty = np.random.randint(10, 100)

                variance = np.random.choice(
                    [0, -1, -2, 1, 2],
                    p=[0.7, 0.1, 0.05, 0.1, 0.05]
                )

                physical_qty = system_qty + variance

                records.append({
                    "count_id": f"CNT-{sku}-{bin_id}-{count_date.strftime('%Y%m')}",
                    "sku_id": sku,
                    "bin_id": bin_id,
                    "count_date": count_date.date(),
                    "count_type": np.random.choice(COUNT_TYPES, p=[0.8, 0.2]),
                    "system_quantity": system_qty,
                    "physical_quantity": physical_qty,
                    "variance_quantity": physical_qty - system_qty,
                    "variance_flag": "MATCH" if variance == 0 else "VARIANCE"
                })

    return pd.DataFrame(records)

skus_list_for_counts = pd.read_csv("skus.csv")["sku_id"].tolist()
bins_list_for_counts = pd.read_csv("bins.csv")["bin_id"].tolist()
start_date_for_counts = datetime.today() - timedelta(days=120)

physical_counts_df = generate_physical_counts(skus_list_for_counts, bins_list_for_counts, start_date_for_counts)
physical_counts_df.to_csv("physical_counts.csv", index=False)

if os.path.exists('physical_counts.csv'):
    print("physical_counts.csv was successfully created.")
else:
    print("Error: physical_counts.csv was not created.")

# --- Final Validation ---
def validate_referential_integrity():
    skus_val = pd.read_csv("skus.csv")
    bins_val = pd.read_csv("bins.csv")
    shipments_val = pd.read_csv("shipments.csv")
    movements_val = pd.read_csv("inventory_movements.csv")
    counts_val = pd.read_csv("physical_counts.csv")

    assert shipments_val["sku_id"].isin(skus_val["sku_id"]).all()
    assert movements_val["sku_id"].isin(skus_val["sku_id"]).all()
    assert counts_val["sku_id"].isin(skus_val["sku_id"]).all()
    assert counts_val["bin_id"].isin(bins_val["bin_id"]).all()

    print("Validation passed: All foreign keys aligned.")

validate_referential_integrity()

