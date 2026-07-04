#!/usr/bin/env python3
"""Generate GeoJSON/TopoJSON/Shapefile/KML/GeoPackage exports for
Nepal's provinces, districts, and local levels, whole-country and
split per province, from the canonical source files in source/.

District boundaries are derived by dissolving local-level (municipality)
polygons by DISTRICT name, since the original district.geojson/topojson
this repo used to ship carried no attributes at all (couldn't be named or
split by province) and have been superseded by this pipeline's output.
STATE_CODE is used as the province join key throughout since the Province
string field is inconsistently encoded (mixes '1'..'7' with province
names like 'Bagmati').

Usage: python3 scripts/generate_datasets.py [source_dir] [out_dir] [manifest_path]
Requires: pip install -r scripts/requirements.txt
"""
import json
import os
import shutil
import sys
import zipfile

import geopandas as gpd
import topojson as tp

SRC_DIR = sys.argv[1] if len(sys.argv) > 1 else "source"
OUT_DIR = sys.argv[2] if len(sys.argv) > 2 else "data"
MANIFEST_PATH = sys.argv[3] if len(sys.argv) > 3 else "_data/datasets.json"

PROVINCE_SLUGS = {
    1: "koshi", 2: "madhesh", 3: "bagmati", 4: "gandaki",
    5: "lumbini", 6: "karnali", 7: "sudurpashchim",
}
PROVINCE_NAMES = {
    1: "Koshi Province", 2: "Madhesh Province", 3: "Bagmati Province",
    4: "Gandaki Province", 5: "Lumbini Province", 6: "Karnali Province",
    7: "Sudurpashchim Province",
}

manifest = {"levels": []}


def human_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def write_all_formats(gdf, base_path, object_name):
    os.makedirs(os.path.dirname(base_path), exist_ok=True)
    sizes = {}

    p = f"{base_path}.geojson"
    gdf.to_file(p, driver="GeoJSON")
    sizes["geojson"] = os.path.getsize(p)

    topo = tp.Topology(gdf, prequantize=1e6, object_name=object_name)
    p = f"{base_path}.topojson"
    with open(p, "w") as f:
        f.write(topo.to_json())
    sizes["topojson"] = os.path.getsize(p)

    tmp_dir = base_path + "__shp_tmp"
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)
    shp_name = os.path.basename(base_path) + ".shp"
    gdf.to_file(os.path.join(tmp_dir, shp_name))
    zip_path = f"{base_path}.shp.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fn in sorted(os.listdir(tmp_dir)):
            zf.write(os.path.join(tmp_dir, fn), fn)
    shutil.rmtree(tmp_dir)
    sizes["shapefile"] = os.path.getsize(zip_path)

    p = f"{base_path}.kml"
    gdf.to_file(p, driver="KML")
    sizes["kml"] = os.path.getsize(p)

    p = f"{base_path}.gpkg"
    gdf.to_file(p, driver="GPKG")
    sizes["gpkg"] = os.path.getsize(p)

    return sizes


def add_manifest_entry(level_key, level_label, scope_key, scope_label, feature_count, sizes, rel_dir):
    manifest.setdefault("_by_level", {})
    lvl = manifest["_by_level"].setdefault(level_key, {"key": level_key, "label": level_label, "scopes": []})
    lvl["scopes"].append({
        "key": scope_key,
        "label": scope_label,
        "feature_count": feature_count,
        "files": {fmt: {"path": f"{rel_dir}/{scope_key}.{ext}", "size": sizes[fmt], "size_human": human_size(sizes[fmt])}
                  for fmt, ext in [("geojson", "geojson"), ("topojson", "topojson"),
                                    ("shapefile", "shp.zip"), ("kml", "kml"), ("gpkg", "gpkg")]},
    })


print("Loading source data...")
gdf_ll = gpd.read_file(os.path.join(SRC_DIR, "municipality.geojson"))
gdf_ll["STATE_CODE"] = gdf_ll["STATE_CODE"].astype(int)
gdf_province = gpd.read_file(os.path.join(SRC_DIR, "province.geojson"))
gdf_province["PROVINCE"] = gdf_province["PROVINCE"].astype(int)
gdf_province["PR_NAME"] = gdf_province["PROVINCE"].map(PROVINCE_NAMES)

print("Dissolving local levels into district boundaries...")
gdf_district = gdf_ll.dissolve(by="DISTRICT", as_index=False).loc[:, ["DISTRICT", "STATE_CODE", "geometry"]]
gdf_district["PR_NAME"] = gdf_district["STATE_CODE"].map(PROVINCE_NAMES)

type_counts = gdf_ll["Type_GN"].value_counts().to_dict()
stats = {
    "provinces": len(gdf_province),
    "districts": len(gdf_district),
    "metropolitan": type_counts.get("Mahanagarpalika", 0),
    "sub_metropolitan": type_counts.get("Upamahanagarpalika", 0),
    "municipality": type_counts.get("Nagarpalika", 0),
    "rural_municipality": type_counts.get("Gaunpalika", 0),
    "protected_areas": sum(v for k, v in type_counts.items()
                            if k not in ("Mahanagarpalika", "Upamahanagarpalika", "Nagarpalika", "Gaunpalika")),
    "total_local_level_features": len(gdf_ll),
}
stats["local_levels"] = stats["metropolitan"] + stats["sub_metropolitan"] + stats["municipality"] + stats["rural_municipality"]
os.makedirs("_data", exist_ok=True)
with open("_data/stats.json", "w") as f:
    json.dump(stats, f, indent=2)

total_files = 0
total_bytes = 0

def track(sizes):
    global total_files, total_bytes
    total_files += len(sizes)
    total_bytes += sum(sizes.values())

# --- Provinces: whole country only ---
rel = "province"
sizes = write_all_formats(gdf_province, os.path.join(OUT_DIR, rel, "nepal"), "provinces")
add_manifest_entry("province", "Provinces", "nepal", "All Nepal (7 provinces)", len(gdf_province), sizes, rel)
track(sizes)

# --- Districts: whole country + per-province ---
rel = "district"
sizes = write_all_formats(gdf_district, os.path.join(OUT_DIR, rel, "nepal"), "districts")
add_manifest_entry("district", "Districts", "nepal", "All Nepal (77 districts)", len(gdf_district), sizes, rel)
track(sizes)

for code, slug in PROVINCE_SLUGS.items():
    subset = gdf_district[gdf_district["STATE_CODE"] == code]
    sizes = write_all_formats(subset, os.path.join(OUT_DIR, rel, slug), "districts")
    add_manifest_entry("district", "Districts", slug, f"{PROVINCE_NAMES[code]} ({len(subset)} districts)", len(subset), sizes, rel)
    track(sizes)

# --- Local levels: whole country + per-province ---
rel = "local-level"
sizes = write_all_formats(gdf_ll, os.path.join(OUT_DIR, rel, "nepal"), "local_levels")
add_manifest_entry("local-level", "Local Levels", "nepal", f"All Nepal ({len(gdf_ll)} units)", len(gdf_ll), sizes, rel)
track(sizes)

for code, slug in PROVINCE_SLUGS.items():
    subset = gdf_ll[gdf_ll["STATE_CODE"] == code]
    sizes = write_all_formats(subset, os.path.join(OUT_DIR, rel, slug), "local_levels")
    add_manifest_entry("local-level", "Local Levels", slug, f"{PROVINCE_NAMES[code]} ({len(subset)} units)", len(subset), sizes, rel)
    track(sizes)

manifest["levels"] = list(manifest.pop("_by_level").values())
os.makedirs(os.path.dirname(MANIFEST_PATH) or ".", exist_ok=True)
with open(MANIFEST_PATH, "w") as f:
    json.dump(manifest, f, indent=2)

print(f"\nDone. {total_files} files written, {human_size(total_bytes)} total.")
