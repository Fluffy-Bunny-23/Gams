# Gams Management Tool

A comprehensive utility for managing your Gams collection. This tool integrates game adding, deleting, duplicate detection, and maintenance into a single script.

## Usage

### Interactive Mode
Run the script without arguments to enter the interactive menu:
```bash
python manage_gams.py
```

### Command Line Mode

**Add a Game:**
```bash
python manage_gams.py add <game_id> [section]
# Example: python manage_gams.py add clslope Unity
```

**Delete a Game:**
```bash
python manage_gams.py delete <game_name>
# Example: python manage_gams.py delete "Slope"
```

**Find Duplicates:**
Scans for duplicate game entries in `Gams.html`.
```bash
python manage_gams.py duplicates
```

**Find Orphaned Files:**
Scans for files in `g/g/` that are not linked in `Gams.html`.
```bash
python manage_gams.py orphans
```

**List Games:**
Lists all installed games organized by section.
```bash
python manage_gams.py list
```

**Backup Configuration:**
Creates a timestamped backup of `Gams.html`.
```bash
python manage_gams.py backup
```

## Features

*   **Integrated Adder:** Uses the UGS database to fetch and install games.
*   **Smart Deletion:** Removes game entries from `Gams.html` and deletes associated files and thumbnails.
*   **Duplicate Detection:** Identifies duplicate game names to keep your list clean.
*   **Orphan Cleanup:** Finds and removes game files that are taking up space but not listed in your library.
*   **Backup:** Easily backup your `Gams.html` configuration.
