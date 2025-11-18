# Game Upload Guide for Gams

This guide provides step-by-step instructions for adding new games to the Gams project. Any AI agent can follow this process to successfully upload and configure games.

## Prerequisites

- Access to the Gams project repository
- Game files (HTML, JS, CSS, assets)
- Game thumbnail/image (PNG format, 200x200px recommended)

## Step 1: Add Game Files

### Location
Place game files in the `/g/g/` directory:
```
/workspaces/Gams/g/g/
```

### File Organization
- **Simple game**: Single HTML file → `/g/g/gamename.html`
- **Complex game**: Multiple files → `/g/g/gamename/` subdirectory
  - Main file: `/g/g/gamename/index.html`
  - Assets: `/g/g/gamename/assets/`, `/g/g/gamename/img/`, etc.

### Examples
```
/g/g/eaglercraft.html           # Simple single-file game
/g/g/drivemad/drivemad.html     # Complex game with subdirectory
/g/g/cookie/index.html          # Complex game with index.html
```

## Step 2: Update Game List Configuration

### Edit the Main Configuration File
Open `/workspaces/Gams/Gams.html` and locate the `gamsList` array (lines 85-471).

### Add Game Entry

#### Option A: Simple Game Entry
For games that follow the standard naming convention:
```javascript
{name: "Game Name"}
```
This automatically links to `g/gamename.html` (lowercase, no spaces).

#### Option B: Custom Path Entry
For games with custom file locations:
```javascript
{name: "Game Name", href: "g/g/gamedirectory/index.html"}
```

#### Option C: Special Type Entry
For tools or special launch modes:
```javascript
{name: "Tool Name", type: "raw"}
```

### Section Organization

#### Add to Existing Section
Place the game entry in the appropriate existing section:
```javascript
{title: "Unity", type: "section"},
{name: "Existing Game"},
{name: "Your New Game"},        // Add here
{name: "Another Existing Game"},
```

#### Create New Section
For organizing custom games:
```javascript
{title: "Custom Games", type: "section"},
{name: "Your Game 1"},
{name: "Your Game 2"},
```

### Section Examples
Current sections in the project:
- Basic
- Unity  
- Retrogaming
- Henry Stickmin Flash
- Flash
- Tools

## Step 3: Add Game Thumbnail

### Image Requirements
- **Format**: PNG
- **Recommended size**: 200x200px
- **Location**: `/workspaces/Gams/img/`

### Naming Convention
The image filename must match the game name:
- Convert to lowercase
- Remove all spaces
- Add `.png` extension

### Examples
| Game Name | Image Filename |
|-----------|----------------|
| "EaglerCraft" | `eaglercraft.png` |
| "Drive Mad" | `drivemad.png` |
| "Cookie Clicker" | `cookieclicker.png` |
| "1 on 1 Soccer" | `1on1soccer.png` |

### Adding the Image
```bash
# Copy image to correct location with correct name
cp /path/to/game-thumbnail.png /workspaces/Gams/img/gamename.png
```

## Step 4: Verification

### Test the Configuration
1. Open `Gams.html` in a browser
2. Search for your game name
3. Verify the thumbnail appears
4. Click the game to test launch
5. Test different launch modes if applicable

### Common Issues to Check
- [ ] Image filename matches naming convention
- [ ] Game path is correct
- [ ] No syntax errors in `gamsList` array
- [ ] Game loads properly in iframe/new tab

## Complete Example

### Adding "EaglerCraft" Game

1. **Add game file**:
   ```bash
   # Place eaglercraft.html in /g/g/
   cp eaglercraft.html /workspaces/Gams/g/g/eaglercraft.html
   ```

2. **Update game list** in `Gams.html`:
   ```javascript
   // Add to appropriate section (e.g., "Unity")
   {title: "Unity", type: "section"},
   {name: "Slope"},
   {name: "EaglerCraft"},  // Add this line
   {name: "Burrito Bison", href: "g/g/burritobison/burritobison.html"},
   ```

3. **Add thumbnail**:
   ```bash
   cp eaglercraft-icon.png /workspaces/Gams/img/eaglercraft.png
   ```

4. **Verify**: Open `Gams.html` and test the game.

## Advanced Options

### Custom Game Types
- `type: "raw"` - Opens directly in new tab
- `href: "custom/path"` - Override default path resolution
- `img: "custom/image.png"` - Override default image path

### Multiple Launch Modes
The system supports these launch modes (user-selectable):
- **gam**: New tab with game wrapper
- **embed**: Embedded on current page
- **blank**: About:blank tab with game
- **direct**: Replace current tab
- **raw**: Direct link (for tools)

## Troubleshooting

### Game Not Appearing
- Check for syntax errors in `gamsList` array
- Verify image exists with correct filename
- Ensure game file path is accessible

### Image Not Loading
- Confirm filename matches naming convention
- Check image is in `/img/` directory
- Verify image format is PNG

### Game Not Loading
- Test game file directly in browser
- Check for missing dependencies (JS, CSS, assets)
- Verify file permissions are correct

## File Structure Reference

```
/workspaces/Gams/
├── Gams.html              # Main configuration (edit gamsList here)
├── g/
│   └── g/                 # Game files directory
│       ├── eaglercraft.html
│       ├── drivemad/
│       │   └── drivemad.html
│       └── cookie/
│           └── index.html
└── img/                   # Game thumbnails
    ├── eaglercraft.png
    ├── drivemad.png
    └── cookieclicker.png
```

Following this guide ensures consistent game integration and proper functionality within the Gams platform.