"""Step 1: Fetch real SPHEREx spectral image cutouts for WISE 0855 from NASA/IPAC IRSA."""

import os
import sys
import time
import astropy.units as u
import pyvo
import requests
from astropy.coordinates import SkyCoord
from astropy.io import fits

# A. Hard-coded target and cutout parameters
TARGET_NAME = "WISE 0855"
TARGET_RA_DEG = 133.795129
TARGET_DEC_DEG = -7.245147
CUTOUT_SIZE_DEG = 0.02
TAP_URL = "https://irsa.ipac.caltech.edu/TAP"
OUTPUT_DIR = "cutouts_wise0855"
MAX_CUTOUTS = 5


def download_cutout(url, dest_path, max_attempts=5):
    """Download a FITS cutout from IRSA IBE, retrying transient 5xx/429 responses."""
    for attempt in range(1, max_attempts + 1):
        resp = requests.get(url, timeout=120)
        if resp.status_code in (429, 500, 502, 503, 504) and attempt < max_attempts:
            wait_sec = int(resp.headers.get("Retry-After", 5))
            time.sleep(wait_sec)
            continue
        resp.raise_for_status()
        if not (resp.content.startswith(b"SIMPLE") or resp.content.startswith(b"\x1f\x8b")):
            raise ValueError(f"Unexpected non-FITS response ({len(resp.content)} bytes)")
        with open(dest_path, "wb") as f:
            f.write(resp.content)
        return


def main():
    coord = SkyCoord(ra=TARGET_RA_DEG * u.degree, dec=TARGET_DEC_DEG * u.degree, frame="icrs")
    size = CUTOUT_SIZE_DEG * u.degree

    # B. Connect to IRSA TAP and run the tutorial ADQL query (oldest observation first)
    query = f"""SELECT
    'https://irsa.ipac.caltech.edu/' || a.uri || '?center={coord.ra.deg},{coord.dec.deg}d&size={size.value}' AS uri,
    p.time_bounds_lower,
    p.energy_bandpassname
FROM spherex.artifact a
JOIN spherex.plane p ON a.planeid = p.planeid
WHERE 1 = CONTAINS(POINT('ICRS', {coord.ra.deg}, {coord.dec.deg}), p.poly)
ORDER BY p.time_bounds_lower"""

    try:
        tap_service = pyvo.dal.TAPService(TAP_URL)
        results = tap_service.search(query).to_table()
    except Exception as exc:
        print(f"TAP query error for {TARGET_NAME}: {exc}")
        print(f"FAILED: IRSA TAP query failed ({exc})")
        sys.exit(1)

    # C. Print how many images were found
    print(f"Target: {TARGET_NAME} (RA={coord.ra.deg}, Dec={coord.dec.deg}, size={size.value} deg)")
    print(f"Number of images found: {len(results)}")
    if len(results) == 0:
        print("FAILED: 0 SPHEREx images found for target")
        sys.exit(1)

    # D. Download cutouts for the first 5 results into cutouts_wise0855/
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    saved_items = []
    for row in results[:MAX_CUTOUTS]:
        uri = str(row["uri"])
        band = str(row["energy_bandpassname"])
        mjd_lower = float(row["time_bounds_lower"])
        filename = uri.split("?", 1)[0].rsplit("/", 1)[-1]
        dest_path = os.path.join(OUTPUT_DIR, filename)
        try:
            download_cutout(uri, dest_path)
            saved_items.append((dest_path, mjd_lower, band))
        except Exception as exc:
            print(f"Download error for {filename}: {exc}")

    # E. Open each saved FITS file with astropy and print one summary line per file
    opened_count = 0
    for path, mjd_lower, band in saved_items:
        try:
            with fits.open(path) as hdul:
                img_hdu = hdul["IMAGE"]
                obs_time = img_hdu.header.get("DATE-OBS", f"MJD {mjd_lower:.6f}")
                detector = img_hdu.header.get("DETECTOR", "unknown")
                shape = img_hdu.data.shape
                print(
                    f"{os.path.basename(path)} | obs_time={obs_time} | "
                    f"band={band} (detector={detector}) | shape={shape}"
                )
                opened_count += 1
        except Exception as exc:
            print(f"FITS read error for {os.path.basename(path)}: {exc}")

    # F. Final status
    if opened_count >= 1:
        print("DONE: real data fetched")
    else:
        print("FAILED: no cutouts were saved and opened successfully")
        sys.exit(1)


if __name__ == "__main__":
    main()
