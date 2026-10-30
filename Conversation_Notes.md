# FS25_Farma9000: conversation notes (2026-10-29)

## 1. Tallest, fattest single tube in the base game (looks only, not capacity)
Sizes are the space each silo needs when placed (its test area), not the exact measurements of the tube:

| Silo | Height | Width | Type |
|---|---|---|---|
| **NL16-22 2000** | **~24 m** | **~16 m** | silo |
| Flat Bottom Bin 3609 | ~14 m | ~12 m | silo |
| Flat Bottom Bin 3608 | ~13 m | ~12 m | silo |
| Flat Bottom Bin 3605 | ~9 m | ~13 m | silo |
| Farma 250 | ~15 m | ~8 m | silo extension |

**Winner: NL16-22 2000**
- Game folder: `G:\SteamLibrary\steamapps\common\Farming Simulator 25\data\placeables\neuero\nl1622_2000\`
- Picture: `MOD PROJECTS\Library\_FS25_Buildings\Silos\Nl 1622 2000\picture.png`

### NL16-22 2000 size
- Straight wall up to **~19 m** (where the top grid ring sits). Roof peak **~24 m**.
- The tube needs a **16 x 16 m** area, so it's a bit under 16 m across (best guess ~14 m).
  Exact width needs measuring in GIANTS Editor.
- The loading shed beside it adds 7 x 13.5 m. The whole silo takes up about 16 x 28.5 m.

## 3. Idea for later: dynamic pipe to the nearest silo (not started)
A pipe on the PRX flat roof top that reaches over to the nearest silo and looks connected. Visual only: the storage link
already works by distance.
1. A Lua script finds the nearest silo in range when the extension is placed, and again when something nearby is placed or sold.
2. The pipe turns toward it, a straight section stretches to the right length and slopes down like a grain spout.
3. The other silo's roof height comes from an invisible ray fired down from above it (the game doesn't store where a silo's top is).
4. An elbow and a short downspout finish it on the other roof.

To work out: texture stretching (repeat pipe sections or keep the texture plain), a range cap (folded on the roof when
nothing is in range), skip silos with no real top (bunker silos, Extension Small/Large). Multiplayer needs no syncing:
each game works it out the same way. Moderate job: the script plus a simple pipe model. Preview first.

## 4. Session of 2026-10-29: vent, new look, machinery parts
**Where it stands:** mod source is at **1.3.0.0**, built but NOT zipped, NOT committed. The last zip sent out
(Testing_local + mods) is 1.2.1.0.

### Done in the mod
1. **Notes cleanup:** old Section 2 removed from this file and from the git history (force-pushed).
2. **Roof vent (1.2.0.0):** one vent next to the ladder top, from your photo, on all three silos; the box behind the
   hood shortened to match the photo 1:1. Stock roof for all three.
3. **Shinier look (1.2.1.0):** wall, roof and pad switched to the game's reflective building shader (same one the base
   bins use; that's why ours looked drab). New concrete pad texture (weathered, grime at the wall foot).
   Tested in game: draws fine.
4. **New wall texture (1.3.0.0):** drawn from scratch in the style of the base-game Neuero NL1622 wall (soft light
   grey, fine corrugation, ~1 m rings, bolt rows, staggered laps). Our own texture, not a copy, on all three silos.
   Rule: pointing to a game texture by its `$data` path is fine; copying GIANTS files into a mod is not.
5. **Half ribs (1.3.0.0):** every other rib stops at half the silo's height (9000 16 m, 8000 12.8 m, 6000 9.6 m).
6. Shop images and icon re-rendered each time. All models pass the format check with 0 problems.
7. The roof textures on disk were changed at 17:21 by someone else; they were left as they are.

### Zips
- 1.2.0.0 and then 1.2.1.0 zipped to Testing_local and mods (you named those two; no server upload).

### Machinery parts (separate, NOT in the mod)
Saved as their own parts in `MOD PROJECTS\Library\_FS25_SiloMachinery\` ("like wheels on a truck": the silo is the
truck, these bolt on and can go in any mod):
- **aerationBlower** (squirrel-cage fan at the wall foot)
- **roofFill** (fill ring, spout, supports; same on every silo)
- **conveyor** (covered drag conveyor with drive and walkway; any length)
- **bucketElevator** (tall leg beside the silo; any height)
- **roofExhaustFan**
- **Kits** for PRX9000 / 8000 / 6000: where each part goes on that silo and at what size.

Plain colours only so far, no textures or fine detail. Kept separate instead of one piece so they fit other silo sizes.

### Rules set this session
- Always ask before taking the screen (GIANTS Editor, screenshots, clicks).
- All knowledge goes in FS25_Universal_Knowledge.md.
- "Build it" = put every agreed change into the mod, but don't zip.

### Next up (not started)
- Fit the machinery kits onto the PRX silos (when you say), then textures/detail on the parts.
- The pipe-to-nearest-silo idea (Section 3).
- Zip 1.3.0.0 when you say; commit when you say.

### Later the same session: machinery on the silos (1.4.0.0, built, not zipped)
- Codex's realism_v2 machinery (blower, roof fill cone, grated conveyor, caged elevator leg) is now ON all three silos.
- Leg cut to each silo: 40.1 / 33.7 / 27.3 m (sections taken out between the platforms, detail untouched).
- Each part is still its own node (visuals > machinery), and the parts still live separately in the Library.
- Placement area widened so nothing can be placed into the leg or blowers (about 30 x 24 m now).
- Shop images and icon show the machinery. No roof exhaust fan (no v2 model yet).
