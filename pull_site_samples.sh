#!/bin/bash
# Run this on the cluster, in the same directory as MioVision_Data.zip
# Pulls ONE representative (~1pm) hourly chunk per shortlisted site into
# site_samples/<SiteName>/ so you can scrub through them locally for
# extra pedestrian/bicycle examples.

set -e
ZIP="MioVision_Data.zip"
OUTDIR="site_samples"
mkdir -p "$OUTDIR"

declare -A SITES=(
  ["Aloma_Path"]="MioVision Data/Bike Lane Study/MioVision Video/Aloma Path"
  ["BL_Edgewater"]="MioVision Data/Bike Lane Study/MioVision Video/BL Edgewater"
  ["BL_Lakemont"]="MioVision Data/Bike Lane Study/MioVision Video/BL Lakemont"
  ["NBL_Lee_Road"]="MioVision Data/Bike Lane Study/MioVision Video/NBL Lee Road"
  ["NBL_Pine_Hills"]="MioVision Data/Bike Lane Study/MioVision Video/NBL Pine Hills"
  ["Rinehart_Road_Path"]="MioVision Data/Bike Lane Study/MioVision Video/Rinehart Road Path"
  ["WORT_Path"]="MioVision Data/Bike Lane Study/MioVision Video/WORT Path"
  ["Pleasant_Hill_Path"]="MioVision Data/Bike Lane Study/MioVision Video/Pleasant Hill Path"
)

for name in "${!SITES[@]}"; do
  path="${SITES[$name]}"
  echo "== $name =="
  mkdir -p "$OUTDIR/$name"
  # pull just the .013 (or .00013) hourly chunk -- 1pm-ish, real daylight traffic
  unzip -j "$ZIP" "$path/*/*.013.mp4" -d "$OUTDIR/$name" 2>/dev/null \
    || unzip -j "$ZIP" "$path/*/*.00013.mp4" -d "$OUTDIR/$name" 2>/dev/null \
    || echo "   (no .013 chunk found for $name -- check all_site_picks.txt for its actual filename)"
done

echo
echo "Done. Contents:"
find "$OUTDIR" -name "*.mp4"
echo
echo "Now from your LOCAL machine:"
echo "  scp -r rmathew1@<cluster-login-host>:$(pwd)/$OUTDIR ./"
