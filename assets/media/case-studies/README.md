# Case study media

## execution-mockup.png
Framed device mockup for the **Execution** section (desktop + phones).

## hero-video.mp4
Original hero screen recording for the device mockup at the top of the case study.

Recommended: MP4 (H.264), **1920px+ wide**, minimal compression.

## overview/
Carousel + grid preview slides for **Project Overview** and **Execution grid**.

- `overview-1.png` … `overview-6.png`

Recommended: PNG or WebP, **2400px+ wide**.

## landing-pages/
Full-length landing page exports for the **Visuals** explorer (Figma-style pan/zoom).

**Desktop** (any of these names work):
- `Homepage.jpg` / `homepage.png`
- `GMC.jpg` / `group-medical.png`
- `Travel.jpg` / `travel-insurance.png`
- `Credit.jpg` / `credit-insurance.png`
- `Gig workers.jpg` / `gig-worker.png`
- `Electronics.jpg` / `electronics.png`
- `Mobile.jpg` / `mobile.png` — **Mobile** tab in Visuals (alongside Homepage, GMC, etc.)

Recommended: JPG or PNG, **1440px wide**, full page height from Figma.

## Rebuild after adding assets

```bash
python3 tools/build_case_study.py
```
