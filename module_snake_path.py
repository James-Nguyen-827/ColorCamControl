import csv


def bilinear_point(tl, tr, bl, br, r_ratio, c_ratio):
    # Interpolate top edge and bottom edge, then between them
    top_x = tl["X"] + (tr["X"] - tl["X"]) * c_ratio
    top_y = tl["Y"] + (tr["Y"] - tl["Y"]) * c_ratio
    top_z = tl["Z"] + (tr["Z"] - tl["Z"]) * c_ratio

    bot_x = bl["X"] + (br["X"] - bl["X"]) * c_ratio
    bot_y = bl["Y"] + (br["Y"] - bl["Y"]) * c_ratio
    bot_z = bl["Z"] + (br["Z"] - bl["Z"]) * c_ratio

    x = top_x + (bot_x - top_x) * r_ratio
    y = top_y + (bot_y - top_y) * r_ratio
    z = top_z + (bot_z - top_z) * r_ratio
    return {"X": x, "Y": y, "Z": z}


def generate_snake_csv(corners, rows, cols, outfile, z_override=None):
    tl = corners["TL"]; tr = corners["TR"]; bl = corners["BL"]; br = corners["BR"]
    with open(outfile, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["image#", "Xcoord", "Ycoord", "Zcoord"])
        idx = 0
        for r in range(rows):
            r_ratio = r / (rows - 1) if rows > 1 else 0
            col_range = range(cols) if r % 2 == 0 else range(cols-1, -1, -1)
            for c in col_range:
                c_ratio = c / (cols - 1) if cols > 1 else 0
                pt = bilinear_point(tl, tr, bl, br, r_ratio, c_ratio)
                if z_override is not None:
                    pt["Z"] = z_override
                writer.writerow([idx, f"{pt['X']:.2f}", f"{pt['Y']:.2f}", f"{pt['Z']:.2f}"])
                idx += 1
