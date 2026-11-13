<p align="center">
  <a href="https://github.com/DTM-Mods"><img src="https://raw.githubusercontent.com/DTM-Mods/.github/main/assets/dtm-header.jpg" alt="DTM Mods by PropaineX & Fennell" width="100%"></a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/DTM-Mods/.github/main/assets/icons/FS25_PRX9000.png" alt="Pro X (PRX) Silo Extensions icon" width="128">
</p>

<h1 align="center">Pro X (PRX) Silo Extensions</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Farming%20Simulator-25-2E6B4F" alt="Farming Simulator 25">
  <a href="https://github.com/DTM-Mods/FS25_PRX9000/releases/latest"><img src="https://img.shields.io/github/v/release/DTM-Mods/FS25_PRX9000?label=version&color=D9A441" alt="Latest version"></a>
  <a href="https://github.com/DTM-Mods"><img src="https://img.shields.io/badge/DTM-Mods-143326" alt="DTM Mods"></a>
</p>

<p align="center">
  <b>Silo extensions up to 10,000,000 L, built from scratch.</b><br>
  <sub>by PropaineX</sub>
</p>

<p align="center">
  <a href="https://github.com/DTM-Mods/FS25_PRX9000/releases/latest"><img src="https://img.shields.io/badge/Download-latest%20release-D9A441?style=for-the-badge&logo=github&logoColor=143326&labelColor=E9C77A" alt="Download the latest release"></a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/DTM-Mods/.github/main/assets/features.jpg" alt="Features" width="100%">
</p>

Farming Simulator 25 silo extensions, built from scratch by PropaineX.

| Item | Walls | Capacity | Price |
|---|---|---|---|
| PRX9000 | 32 m | 10,000,000 L | $450,000 |
| PRX8000 | 25.6 m | 8,000,000 L | $360,000 |
| PRX6000 | 19.2 m | 6,000,000 L | $270,000 |

- All 18 m wide, holding farm silo goods
- Corrugated galvanised steel with vertical ribs, ring seams every 3.2 m, a flat-topped roof and a caged ladder
- Standing on a weathered concrete foundation pad
- Shop: Buildings > Silo Extensions

<!-- dtm-screenshots -->

<p align="center">
  <img src="https://raw.githubusercontent.com/DTM-Mods/.github/main/assets/screenshots.jpg" alt="Screenshots" width="100%">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/DTM-Mods/.github/main/assets/screens/FS25_PRX9000/shop.jpg" alt="PRX6000, PRX8000 and PRX9000" width="100%">
</p>

<!-- /dtm-screenshots -->

<p align="center">
  <img src="https://raw.githubusercontent.com/DTM-Mods/.github/main/assets/installation.jpg" alt="Installation" width="100%">
</p>

Download `FS25_PRX9000.zip` from the [latest release](https://github.com/DTM-Mods/FS25_PRX9000/releases/latest) and put it in `Documents/My Games/FarmingSimulator2025/mods`, without unzipping or renaming it. In multiplayer, the server and every player need the same version.

## Patch notes

### 1.7.3.0 - 2026-11-11 - Onions, bananas and coffee

- PRX9000, PRX8000 and PRX6000 now also store onions (clean and dirty), bananas and coffee cherries. The silo crop list matches the Fed Mods silos again (75 crops).
- Bananas and coffee cherries come with the Beans & Alpacas DLC; on maps without them they're simply skipped.
- Untested in the running game.

[Full patch history](PATCH_NOTES.md).

<p align="center">
  <img src="https://raw.githubusercontent.com/DTM-Mods/.github/main/assets/license.jpg" alt="License" width="100%">
</p>

MIT, see [LICENSE](LICENSE). Anything here that comes from Farming Simulator 25 or its DLC (models, textures, sounds and other game files) belongs to GIANTS Software and is not covered by it.

<details>
<summary><b>For developers</b>: files, building and tests</summary>

### Files

- `modDesc.xml`, `prx9000.xml`, `prx8000.xml`, `prx6000.xml`: mod and placeable definitions
- `models/`: the three models
- `textures/`: corrugated steel textures for the wall and roof, concrete for the foundation pad, machinery textures
- `reference/`: the look we're aiming for
- `tools/`: texture conversion and a concrete normal-map regression check; excluded from the mod ZIP
- [Concrete movement diagnosis and engine comparison](docs/concrete-pad-parallax.md)

### Concrete texture tools

`python tools/verify_concrete_normal.py` checks the shipped concrete normal map for accidental parallax data.
`python tools/png_to_dds.py input_normal.png output_normal.dds` preserves RGB normal maps as three-channel BC1;
RGBA normal maps retain their intentional height channel. Use `--normal-rgb` explicitly when a normal map has an
unused opaque alpha channel. Other texture types retain the existing DXT5 conversion behavior.

</details>

---

<p align="center">
  <a href="https://github.com/DTM-Mods"><img src="https://raw.githubusercontent.com/DTM-Mods/.github/main/assets/dtm-intro.gif" alt="DTM Mods by PropaineX & Fennell" width="420"></a><br>
  <sub>Part of <a href="https://github.com/DTM-Mods">DTM Mods</a> (Designed To Manage) by PropaineX & Fennell</sub>
</p>
