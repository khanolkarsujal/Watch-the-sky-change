# See the Sky Change

A web tool that shows real NASA SPHEREx images of a patch of sky as a short animation, so the viewer can see objects move over time.

Built as a hackathon demo. It uses real SPHEREx data only. No simulated or placeholder imagery is used.

## Overview

SPHEREx observes the whole sky repeatedly, so the same region is imaged at different times. Objects that move across the sky, such as nearby stars and brown dwarfs, appear at slightly different positions from one observation to the next.

This tool retrieves those observations for a chosen location and plays them in time order, so the motion is visible without any specialist software or knowledge.

## Features

**1. Watch the sky change**
Enter a star name or RA/Dec coordinates. The tool fetches SPHEREx image cutouts for that location and plays them as an animation.

**2. Explore stars**
A curated set of stars, each with imagery and a short description of how it moves. Selecting one loads it into the viewer.

## How It Works

1. The user enters a star name or RA/Dec coordinates (decimal degrees).
2. A star name is resolved to coordinates.
3. The backend queries the NASA/IPAC Infrared Science Archive (IRSA) for SPHEREx images covering that position.
4. FITS cutouts around the target are downloaded.
5. Frames are ordered by observation time and rendered.
6. The browser plays the frames as a short animation.

## Example Targets

| Target | Note |
|---|---|
| Barnard's Star | Nearby red dwarf with a very large proper motion |
| WISE 0855 | Extremely cold brown dwarf |
| Epsilon Indi B | Nearby brown dwarf |
| RW Aurigae | Young variable star |
| R Draconis | Variable star |

## Running the Demo

```bash
# Backend
pip install -r requirements.txt
python <backend-entry-file>.py

# Front end
npm install
npm run dev
```

Internet access is required to reach the IRSA archive.

## Data Source

- Mission: NASA SPHEREx
- Archive: NASA/IPAC Infrared Science Archive (IRSA)

This project is an independent hackathon demo and is not an official NASA product.
