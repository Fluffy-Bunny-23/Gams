# Gams Game Adder CLI Tool

A powerful CLI tool to automatically add games from UGS (Universal Game Site) to your Gams collection.

## Features

- 🔍 **Search** games from UGS database (1700+ games)
- 📂 **Browse** games by letter
- 🎮 **Auto-download** and install games
- 🖼️ **Auto-generate** thumbnails using Gams logo
- 📋 **Auto-add** to game list in correct section
- 🎯 **Interactive** and command-line modes

## Quick Start

### Interactive Mode (Recommended)
```bash
python gams_adder.py
```

This launches an interactive menu where you can:
1. Search for games
2. Browse by letter  
3. Select section and add games

### Command Line Mode

#### Add a specific game:
```bash
python gams_adder.py add <game_id> [section] [--custom-img]
```

Examples:
```bash
# Add 2048 to Basic section
python gams_adder.py add cl2048 Basic

# Add Mario to Unity section with custom image
python gams_adder.py add clmario3 Unity --custom-img
```

#### Search for games:
```bash
python gams_adder.py search <query>
```

Examples:
```bash
python gams_adder.py search mario
python gams_adder.py search "car racing"
python gams_adder.py search zombie
```

## Available Sections

- `Custom` - For custom games
- `Basic` - Simple HTML5 games
- `Unity` - Unity WebGL games  
- `Retrogaming` - Retro/Emulated games
- `Henry Stickmin Flash` - Henry Stickmin series
- `Flash` - Flash games
- `Tools` - Utilities and tools

## Game IDs

Games use UGS IDs with `cl` prefix:
- `cl2048` → 2048 game
- `clmario3` → Mario 3
- `clslope` → Slope
- `clcookieclicker` → Cookie Clicker

Use the search function to find game IDs.

## What the Tool Does

1. **Downloads** game HTML from UGS CDN
2. **Saves** game file to `/g/g/` directory
3. **Creates** thumbnail using Gams logo (unless `--custom-img`)
4. **Updates** `Gams.html` game list
5. **Organizes** in selected section

## Examples

### Adding a Popular Game
```bash
# Search for slope games
python gams_adder.py search slope

# Add Slope 2 to Unity section
python gams_adder.py add clslope2 Unity
```

### Adding Multiple Games
```bash
# Add classic games
python gams_adder.py add clpacman Basic
python gams_adder.py add cltetris Basic  
python gams_adder.py add clpacman Flash
```

### Using Interactive Mode
```bash
python gams_adder.py

# Then follow the prompts:
# 1. Search for a game
# 🔍 Enter search term: mario
# 
# 📋 Found 15 games:
#  1. Catmario
#  2. Drmario  
#  3. Mario3
#  4. Mariokart64
# 
# Select game (1-10): 3
# 
# 📂 Available sections:
# 1. Custom
# 2. Basic
# 3. Unity
# 4. Retrogaming
# 
# Select section (1-7): 4
# Use custom image? (y/N): n
# 
# 🎉 Successfully added 'Mario3' to Gams!
```

## File Structure

The tool creates/updates these files:

```
/workspaces/Gams/
├── g/g/
│   ├── 2048.html          # Downloaded game
│   ├── mario3.html        # Downloaded game
│   └── slope2.html        # Downloaded game
├── img/
│   ├── 2048.png           # Auto-generated thumbnail
│   ├── mario3.png         # Auto-generated thumbnail  
│   └── slope2.png         # Auto-generated thumbnail
└── Gams.html              # Updated with new games
```

## Custom Images

If you have custom game thumbnails:
1. Skip auto-generation with `--custom-img`
2. Manually place your image in `/img/` directory
3. Use naming convention: `gamename.png` (lowercase, no spaces)

## Troubleshooting

### Game Not Found
```bash
# Search for similar names
python gams_adder.py search "partial name"
```

### Download Failed
- Check internet connection
- Verify game ID exists
- Try again (temporary CDN issues)

### Section Not Found
- Use exact section name from list
- Case-sensitive (use "Basic" not "basic")

### Image Issues
- Default Gams logo used automatically
- For custom images: place in `/img/` with correct name

## Tips

1. **Use search first** to find exact game IDs
2. **Choose appropriate sections** for better organization
3. **Test games** after adding to ensure they work
4. **Use interactive mode** for discovering new games
5. **Batch add** multiple games from same series

## Advanced Usage

### Adding Games with Custom Paths
If you need custom file organization:
```bash
# Manually edit Gams.html after adding
# Change href: "g/g/gamename.html" 
# To: href: "g/g/customfolder/index.html"
```

### Bulk Operations
Create a script to add multiple games:
```bash
#!/bin/bash
games=("cl2048" "cltetris" "clpacman")
for game in "${games[@]}"; do
    python gams_adder.py add "$game" Basic
done
```

## Support

- **UGS Source**: https://cdn.jsdelivr.net/gh/bubbls/ugs-singlefile@main/AASINGLEFILE.html
- **Game Count**: 1700+ games available
- **Updates**: Games list updates automatically from UGS

Enjoy expanding your Gams collection! 🎮