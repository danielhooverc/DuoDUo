from flask import Flask, render_template
import random


def generate_warehouse_layout(rows, bays, levels, positions):
    warehouse = []
    for r in range(rows):
        row = []
        for b in range(bays):
            bay = []
            for l in range(levels):
                level = []
                for p in range(positions):
                    status = random.choice(["Available", "Occupied", "N/A"])
                    position_label = chr(65 + (p % 3))  # A, B, C循环
                    level.append({"status": status, "label": position_label})
                bay.append(level)
            row.append({"bay_name": f"Bay-{b+1}", "levels": bay})
        warehouse.append({"row_name": f"Row-{r+1}", "bays": row})
    return warehouse