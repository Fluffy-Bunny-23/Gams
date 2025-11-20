#!/usr/bin/env python3
"""
Gams Master Management Script
Integrates game adding, deleting, and maintenance tasks.
"""

import os
import sys
import re
import json
import shutil
import requests
import time
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Dict, Optional, Tuple

# --- GamsGameAdder Logic (Integrated) ---

class GamsManager:
    def __init__(self):
        self.base_dir = Path("/workspaces/Gams")
        self.games_dir = self.base_dir / "g" / "g"
        self.img_dir = self.base_dir / "img"
        self.gams_html = self.base_dir / "Gams.html"
        self.ugs_base_url = "https://cdn.jsdelivr.net/gh/bubbls/ugs-singlefile"
        self.default_image = self.img_dir / "gams.png"
        
        # Available sections from Gams.html
        self.sections = [
            "Custom",
            "Basic", 
            "Unity",
            "Retrogaming",
            "Henry Stickmin Flash",
            "Flash",
            "Tools"
        ]
        
        # Cache for UGS games list
        self.ugs_games = []

    def clear_screen(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    # --- Adder Functionality ---

    def load_ugs_games(self) -> List[str]:
        """Load the list of games from UGS source."""
        if self.ugs_games:
            return self.ugs_games
            
        try:
            url = "https://cdn.jsdelivr.net/gh/bubbls/ugs-singlefile@main/AASINGLEFILE.html"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Extract games list from JavaScript
            content = response.text
            games_match = re.search(r'const files = \[(.*?)\];', content, re.DOTALL)
            
            if games_match:
                games_text = games_match.group(1)
                # Extract all quoted strings
                games = re.findall(r"'([^']+)'", games_text)
                self.ugs_games = [game for game in games if game.startswith('cl')]
                print(f"✓ Loaded {len(self.ugs_games)} games from UGS")
                return self.ugs_games
            else:
                print("✗ Could not find games list in UGS source")
                return []
                
        except Exception as e:
            print(f"✗ Error loading UGS games: {e}")
            return []
    
    def search_games(self, query: str) -> List[str]:
        """Search for games by name."""
        games = self.load_ugs_games()
        query = query.lower()
        
        matches = []
        for game in games:
            # Remove 'cl' prefix for searching
            clean_name = game[2:] if game.startswith('cl') else game
            if query in clean_name.lower():
                matches.append(game)
        
        return matches
    
    def get_game_name(self, game_id: str) -> str:
        """Convert UGS game ID to readable name."""
        if game_id.startswith('cl'):
            clean_name = game_id[2:]
        else:
            clean_name = game_id
            
        # Add spaces and capitalize
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', clean_name)
        name = re.sub(r'([0-9])([a-zA-Z])', r'\1 \2', name)
        name = ' '.join(word.capitalize() for word in name.split())
        
        return name
    
    def download_game(self, game_id: str) -> Optional[str]:
        """Download game HTML from UGS."""
        try:
            url = f"{self.ugs_base_url}/{game_id}.html"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            print(f"✗ Error downloading {game_id}: {e}")
            return None
    
    def save_game_file(self, game_id: str, content: str) -> Path:
        """Save game file to appropriate location."""
        # Use game_id as filename (remove 'cl' prefix)
        filename = f"{game_id}.html"
        if game_id.startswith('cl'):
            filename = f"{game_id[2:]}.html"
            
        filepath = self.games_dir / filename
        
        # Create directory if it doesn't exist
        self.games_dir.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def create_game_image(self, game_name: str) -> Path:
        """Create game thumbnail using default Gams logo."""
        # Convert game name to filename
        img_filename = f"{game_name.lower().replace(' ', '')}.png"
        img_path = self.img_dir / img_filename
        
        # Copy default image if it doesn't exist
        if not img_path.exists() and self.default_image.exists():
            shutil.copy2(self.default_image, img_path)
            print(f"✓ Created thumbnail: {img_path}")
        
        return img_path
    
    def find_section_in_gams_list(self, section: str) -> int:
        """Find the line number where a section starts in gamsList."""
        try:
            with open(self.gams_html, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            section_pattern = f'{{title: "{section}", type: "section"}}'
            
            for i, line in enumerate(lines):
                if section_pattern in line:
                    return i + 1  # Return 1-based line number
            
            return -1
            
        except Exception as e:
            print(f"✗ Error finding section: {e}")
            return -1
    
    def add_game_to_gams_list(self, game_name: str, section: str, custom_path: Optional[str] = None) -> bool:
        """Add game to the gamsList array in Gams.html."""
        try:
            with open(self.gams_html, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the section
            section_line = self.find_section_in_gams_list(section)
            if section_line == -1:
                print(f"✗ Section '{section}' not found")
                return False
            
            lines = content.split('\n')
            
            # Find the end of the section (next section or end of array)
            insert_line = section_line
            for i in range(section_line, len(lines)):
                line = lines[i].strip()
                if line.startswith('{title:') and i > section_line:
                    break
                if line == '];':
                    break
                insert_line = i + 1
            
            # Create game entry
            if custom_path:
                game_entry = f'{{name: "{game_name}", href: "{custom_path}"}}'
            else:
                game_entry = f'{{name: "{game_name}"}}'
            
            # Insert the game entry
            lines.insert(insert_line, f'  {game_entry},')
            
            # Write back to file
            with open(self.gams_html, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print(f"✓ Added '{game_name}' to '{section}' section")
            return True
            
        except Exception as e:
            print(f"✗ Error adding game to gamsList: {e}")
            return False
    
    def add_game(self, game_id: str, section: str, use_custom_image: bool = False) -> bool:
        """Add a complete game to Gams."""
        game_name = self.get_game_name(game_id)
        return self.add_game_with_name(game_id, game_name, section, use_custom_image)
    
    def add_game_with_name(self, game_id: str, game_name: str, section: str, use_custom_image: bool = False) -> bool:
        """Add a complete game to Gams with custom name."""
        print(f"\n🎮 Adding game: {game_id}")
        print(f"📝 Game name: {game_name}")
        
        # Download game
        print("⬇️  Downloading game...")
        content = self.download_game(game_id)
        if not content:
            return False
        
        # Save game file
        print("💾 Saving game file...")
        game_path = self.save_game_file(game_id, content)
        print(f"✓ Saved to: {game_path}")
        
        # Create custom path for gamsList
        custom_path = f"g/g/{game_path.name}"
        
        # Create thumbnail
        if not use_custom_image:
            print("🖼️  Creating thumbnail...")
            self.create_game_image(game_name)
        else:
            print("⏭️  Skipping thumbnail (will use custom)")
        
        # Add to gamsList
        print("📋 Adding to game list...")
        success = self.add_game_to_gams_list(game_name, section, custom_path)
        
        if success:
            print(f"🎉 Successfully added '{game_name}' to Gams!")
            return True
        else:
            print(f"❌ Failed to add '{game_name}'")
            return False

    # --- Deletion Functionality ---

    def parse_gams_list(self) -> List[Dict]:
        """Parse the gamsList from Gams.html into a structured list."""
        try:
            with open(self.gams_html, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = re.search(r'var gamsList = \[(.*?)\];', content, re.DOTALL)
            if not match:
                print("✗ Could not find gamsList in Gams.html")
                return []
            
            list_content = match.group(1)
            
            # This is a simple parser for the JS object format used in Gams.html
            # It assumes objects are separated by commas and properties are clear
            # Ideally we would use a JS parser, but regex will suffice for this specific file structure
            entries = []
            
            # Split by closing brace and comma to separate objects
            # We need to be careful about the splitting
            raw_entries = re.findall(r'\{[^{}]+\}', list_content)
            
            for raw in raw_entries:
                entry = {}
                # Extract name
                name_match = re.search(r'name:\s*"([^"]+)"', raw)
                if name_match:
                    entry['name'] = name_match.group(1)
                
                # Extract href
                href_match = re.search(r'href:\s*"([^"]+)"', raw)
                if href_match:
                    entry['href'] = href_match.group(1)
                    
                # Extract title (for sections)
                title_match = re.search(r'title:\s*"([^"]+)"', raw)
                if title_match:
                    entry['title'] = title_match.group(1)
                    entry['type'] = 'section'
                
                entries.append(entry)
                
            return entries
            
        except Exception as e:
            print(f"✗ Error parsing Gams list: {e}")
            return []

    def delete_game(self, game_name: str) -> bool:
        """Delete a game from Gams.html and filesystem."""
        print(f"\n🗑️  Deleting game: {game_name}")
        
        try:
            with open(self.gams_html, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            new_lines = []
            deleted = False
            game_href = None
            
            # Find and remove line from Gams.html
            for line in lines:
                if f'name: "{game_name}"' in line:
                    deleted = True
                    # Try to extract href to delete file
                    href_match = re.search(r'href:\s*"([^"]+)"', line)
                    if href_match:
                        game_href = href_match.group(1)
                    else:
                        # Fallback to default path: g/<name>.html
                        img_name = game_name.lower().replace(' ', '')
                        game_href = f"g/{img_name}.html"
                    continue
                new_lines.append(line)
            
            if not deleted:
                print(f"✗ Game '{game_name}' not found in Gams.html")
                return False
            
            # Write updated Gams.html
            with open(self.gams_html, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print("✓ Removed entry from Gams.html")
            
            # Delete files
            if game_href:
                # Resolve path relative to workspace root
                # href is usually like "g/g/game.html"
                file_path = self.base_dir / game_href
                
                if file_path.exists():
                    # If it's a directory (some Unity games), delete directory
                    if file_path.is_dir():
                        shutil.rmtree(file_path)
                        print(f"✓ Deleted directory: {file_path}")
                    else:
                        # Check if it's inside a subdirectory in g/g/ that should also be deleted
                        # E.g., g/g/cookie/index.html -> delete g/g/cookie/
                        parts = Path(game_href).parts
                        if len(parts) > 3 and parts[0] == 'g' and parts[1] == 'g':
                            # It's in a subdir like g/g/subdir/file.html
                            subdir = self.base_dir / parts[0] / parts[1] / parts[2]
                            if subdir.exists() and subdir.is_dir():
                                shutil.rmtree(subdir)
                                print(f"✓ Deleted game directory: {subdir}")
                            else:
                                os.remove(file_path)
                                print(f"✓ Deleted file: {file_path}")
                        else:
                            os.remove(file_path)
                            print(f"✓ Deleted file: {file_path}")
                else:
                    print(f"⚠️  File not found at {file_path}")
            
            # Delete thumbnail
            img_name = game_name.lower().replace(' ', '') + ".png"
            img_path = self.img_dir / img_name
            if img_path.exists():
                os.remove(img_path)
                print(f"✓ Deleted thumbnail: {img_path}")
                
            print(f"🎉 Successfully deleted '{game_name}'")
            return True
            
        except Exception as e:
            print(f"✗ Error deleting game: {e}")
            return False

    # --- Duplicate Management ---

    def find_duplicates(self):
        """Find duplicate entries in Gams.html."""
        self.clear_screen()
        print("\n🔍 Scanning for duplicates...")
        entries = self.parse_gams_list()
        
        seen_names = {}
        duplicates = []
        
        for entry in entries:
            if 'name' in entry:
                name = entry['name']
                if name in seen_names:
                    duplicates.append(name)
                else:
                    seen_names[name] = True
        
        if duplicates:
            print(f"⚠️  Found {len(duplicates)} duplicate game names:")
            for name in duplicates:
                print(f"  - {name}")
                
            if input("\nDelete duplicates? (y/N): ").lower().startswith('y'):
                self.remove_duplicates(duplicates)
        else:
            print("✓ No duplicate names found.")
            input("\nPress Enter to continue...")

    def remove_duplicates(self, duplicate_names: List[str]):
        """Remove duplicate entries, keeping the first one."""
        try:
            with open(self.gams_html, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            new_lines = []
            seen = set()
            
            for line in lines:
                is_duplicate_line = False
                for name in duplicate_names:
                    if f'name: "{name}"' in line:
                        if name in seen:
                            is_duplicate_line = True
                            print(f"  - Removing duplicate line for '{name}'")
                        else:
                            seen.add(name)
                        break
                
                if not is_duplicate_line:
                    new_lines.append(line)
            
            with open(self.gams_html, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
                
            print("✓ Duplicates removed from Gams.html")
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"✗ Error removing duplicates: {e}")

    def find_orphaned_files(self):
        """Find files in g/g/ that are not linked in Gams.html."""
        self.clear_screen()
        print("\n🔍 Scanning for orphaned files...")
        entries = self.parse_gams_list()
        linked_files = set()
        
        # Explicit whitelist for system files/dirs
        whitelist = {
            "Gam.html", "misc", "Ruffle", "webretro", "assets", "img"
        }
        
        for entry in entries:
            if 'href' in entry:
                # Normalize path
                path_str = entry['href'].replace('/', os.sep)
                # We only care about the filename or the directory in g/g/
                parts = Path(path_str).parts
                if len(parts) > 2 and parts[0] == 'g' and parts[1] == 'g':
                    # If it points to a file, add the file
                    # If it points to a dir (e.g. g/g/slope2/index.html), add the slope2 dir
                    if len(parts) > 3:
                        linked_files.add(parts[2]) # Add directory name
                    else:
                        linked_files.add(parts[2]) # Add filename
        
        orphans = []
        for item in self.games_dir.iterdir():
            if item.name not in linked_files and item.name not in whitelist:
                orphans.append(item)
        
        if orphans:
            print(f"⚠️  Found {len(orphans)} orphaned items in g/g/:")
            for item in orphans:
                print(f"  - {item.name} ({'DIR' if item.is_dir() else 'FILE'})")
            
            if input("\nDelete orphaned files? (y/N): ").lower().startswith('y'):
                for item in orphans:
                    try:
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            os.remove(item)
                        print(f"  ✓ Deleted {item.name}")
                    except Exception as e:
                        print(f"  ✗ Error deleting {item.name}: {e}")
            input("\nPress Enter to continue...")
        else:
            print("✓ No orphaned files found.")
            input("\nPress Enter to continue...")

    def assign_game_image(self, game_name: str, image_source: Optional[str] = None) -> bool:
        """Assign an image to a specific game (default Gams logo or custom URL)."""
        self.clear_screen()
        print(f"\n🖼️  Assigning image to: {game_name}")
        
        # Convert game name to filename
        img_filename = f"{game_name.lower().replace(' ', '')}.png"
        img_path = self.img_dir / img_filename
        
        try:
            if image_source:
                # Custom URL provided
                print(f"📥 Downloading image from: {image_source}")
                response = requests.get(image_source, timeout=15)
                response.raise_for_status()
                
                with open(img_path, 'wb') as f:
                    f.write(response.content)
                print(f"✓ Downloaded and assigned custom thumbnail: {img_path}")
            else:
                # Use default Gams logo
                if not self.default_image.exists():
                    print(f"✗ Default Gams logo not found at {self.default_image}")
                    input("\nPress Enter to continue...")
                    return False
                
                shutil.copy2(self.default_image, img_path)
                print(f"✓ Assigned default thumbnail: {img_path}")
            
            input("\nPress Enter to continue...")
            return True
            
        except Exception as e:
            print(f"✗ Error assigning image: {e}")
            input("\nPress Enter to continue...")
            return False

    def backup_config(self):
        """Create a backup of Gams.html."""
        self.clear_screen()
        timestamp = int(time.time())
        backup_path = self.base_dir / f"Gams.html.bak.{timestamp}"
        try:
            shutil.copy2(self.gams_html, backup_path)
            print(f"✓ Backup created: {backup_path}")
            input("\nPress Enter to continue...")
            return True
        except Exception as e:
            print(f"✗ Backup failed: {e}")
            input("\nPress Enter to continue...")
            return False

    # --- Main Interface ---

    def interactive_menu(self):
        """Main interactive menu."""
        while True:
            self.clear_screen()
            print("\n🎮 Gams Management Console")
            print("=" * 50)
            print("1. Add New Game")
            print("2. Delete Game")
            print("3. Find Duplicates")
            print("4. Clean Orphaned Files")
            print("5. List All Games")
            print("6. Assign Default Image")
            print("7. Backup Gams.html")
            print("8. Exit")
            
            choice = input("\nSelect option (1-8): ").strip()
            
            if choice == '1':
                self.interactive_add_menu()
            elif choice == '2':
                self.interactive_delete_menu()
            elif choice == '3':
                self.find_duplicates()
            elif choice == '4':
                self.find_orphaned_files()
            elif choice == '5':
                self.list_installed_games()
            elif choice == '6':
                self.interactive_assign_image_menu()
            elif choice == '7':
                self.backup_config()
            elif choice == '8':
                self.clear_screen()
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option")
                time.sleep(1)

    def interactive_add_menu(self):
        """Sub-menu for adding games."""
        self.clear_screen()
        print("\n➕ Add Game Menu")
        print("1. Search for a game")
        print("2. Browse by letter")
        print("3. Back to Main Menu")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            self.search_and_add()
        elif choice == '2':
            self.browse_by_letter()
        elif choice == '3':
            return
        else:
            print("❌ Invalid option")
            time.sleep(1)

    def interactive_delete_menu(self):
        """Sub-menu for deleting games."""
        self.clear_screen()
        print("\n🗑️  Delete Game Menu")
        entries = self.parse_gams_list()
        games = [e['name'] for e in entries if 'name' in e]
        
        print(f"Found {len(games)} installed games.")
        search = input("Enter game name to search (or ENTER to list all): ").strip().lower()
        
        matches = [g for g in games if search in g.lower()]
        
        if not matches:
            print("No games found.")
            input("\nPress Enter to continue...")
            return
            
        print("\nSelect game to delete:")
        for i, game in enumerate(matches[:20], 1):
            print(f"{i}. {game}")
        if len(matches) > 20:
            print(f"...and {len(matches)-20} more")
            
        try:
            sel = input("\nSelect number (0 to cancel): ").strip()
            if not sel or sel == '0':
                return
                
            idx = int(sel) - 1
            if 0 <= idx < len(matches):
                game_to_delete = matches[idx]
                confirm = input(f"Are you sure you want to delete '{game_to_delete}'? (yes/no): ")
                if confirm.lower() == 'yes':
                    self.delete_game(game_to_delete)
                    input("\nPress Enter to continue...")
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Invalid input")

    def interactive_assign_image_menu(self):
        """Sub-menu for assigning default image to games."""
        self.clear_screen()
        print("\n🖼️  Assign Image Menu")
        entries = self.parse_gams_list()
        games = [e['name'] for e in entries if 'name' in e]
        
        print(f"Found {len(games)} installed games.")
        search = input("Enter game name to search (or ENTER to list all): ").strip().lower()
        
        matches = [g for g in games if search in g.lower()]
        
        if not matches:
            print("No games found.")
            input("\nPress Enter to continue...")
            return
            
        print("\nSelect game to assign image:")
        for i, game in enumerate(matches[:20], 1):
            print(f"{i}. {game}")
        if len(matches) > 20:
            print(f"...and {len(matches)-20} more")
            
        try:
            sel = input("\nSelect number (0 to cancel): ").strip()
            if not sel or sel == '0':
                return
                
            idx = int(sel) - 1
            if 0 <= idx < len(matches):
                game_to_update = matches[idx]
                
                # Ask for image source
                print("\nImage source options:")
                print("1. Use default Gams logo")
                print("2. Provide custom image URL")
                
                img_choice = input("Select option (1-2): ").strip()
                
                if img_choice == '1':
                    self.assign_game_image(game_to_update)
                elif img_choice == '2':
                    url = input("Enter image URL: ").strip()
                    if url:
                        self.assign_game_image(game_to_update, url)
                    else:
                        print("❌ No URL provided")
                else:
                    print("❌ Invalid option")
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Invalid input")

    def list_installed_games(self):
        """List all games currently in Gams.html."""
        self.clear_screen()
        entries = self.parse_gams_list()
        current_section = "Uncategorized"
        
        print("\n📋 Installed Games:")
        for entry in entries:
            if entry.get('type') == 'section':
                current_section = entry.get('title', 'Unknown Section')
                print(f"\n--- {current_section} ---")
            elif 'name' in entry:
                print(f"  • {entry['name']}")
        
        print(f"\nTotal entries: {len([e for e in entries if 'name' in e])}")
        input("\nPress Enter to continue...")

    # Copy of helper methods from original adder for compatibility
    def search_and_add(self):
        query = input("🔍 Enter search term: ").strip()
        if not query: return
        matches = self.search_games(query)
        if not matches:
            print("❌ No games found")
            input("\nPress Enter to continue...")
            return
        print(f"\n📋 Found {len(matches)} games:")
        for i, game in enumerate(matches[:10], 1):
            name = self.get_game_name(game)
            print(f"{i:2d}. {name}")
        if len(matches) > 10: print(f"... and {len(matches) - 10} more")
        try:
            selection = input(f"\nSelect game (1-{min(10, len(matches))}): ").strip()
            idx = int(selection) - 1
            if 0 <= idx < min(10, len(matches)):
                self.process_game_selection(matches[idx])
        except ValueError: print("❌ Invalid input")

    def browse_by_letter(self):
        games = self.load_ugs_games()
        letters = sorted(set(game[2:3].upper() if game.startswith('cl') and len(game) > 2 else 'A' for game in games))
        print(f"\n📚 Available letters: {' '.join(letters)}")
        letter = input("🔤 Enter letter: ").strip().upper()
        if letter not in letters:
            print("❌ Invalid letter")
            input("\nPress Enter to continue...")
            return
        filtered = [game for game in games if game.startswith('cl') and len(game) > 2 and game[2:3].upper() == letter]
        print(f"\n📋 Games starting with '{letter}':")
        for i, game in enumerate(filtered[:10], 1):
            name = self.get_game_name(game)
            print(f"{i:2d}. {name}")
        try:
            selection = input(f"\nSelect game (1-{min(10, len(filtered))}): ").strip()
            idx = int(selection) - 1
            if 0 <= idx < min(10, len(filtered)):
                self.process_game_selection(filtered[idx])
        except ValueError: print("❌ Invalid input")

    def process_game_selection(self, game_id: str):
        default_name = self.get_game_name(game_id)
        print(f"\n🎮 Selected: {default_name}")
        
        # Ask for custom name
        custom_name = input(f"Enter game name (press ENTER for '{default_name}'): ").strip()
        game_name = custom_name if custom_name else default_name
        
        print("📂 Available sections:")
        for i, section in enumerate(self.sections, 1):
            print(f"{i}. {section}")
        try:
            section_choice = input(f"Select section (1-{len(self.sections)}): ").strip()
            idx = int(section_choice) - 1
            if 0 <= idx < len(self.sections):
                section = self.sections[idx]
                custom_img = input("Use custom image? (y/N): ").strip().lower()
                self.add_game_with_name(game_id, game_name, section, custom_img.startswith('y'))
                input("\nPress Enter to continue...")
            else:
                print("❌ Invalid section")
        except ValueError: print("❌ Invalid input")


def main():
    manager = GamsManager()
    
    if len(sys.argv) > 1:
        # Simple CLI arguments handling
        cmd = sys.argv[1]
        if cmd == 'add' and len(sys.argv) >= 3:
            manager.add_game(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "Custom")
        elif cmd == 'delete' and len(sys.argv) >= 3:
            manager.delete_game(sys.argv[2])
        elif cmd == 'duplicates':
            manager.find_duplicates()
        elif cmd == 'orphans':
            manager.find_orphaned_files()
        elif cmd == 'list':
            manager.list_installed_games()
        elif cmd == 'assign-image' and len(sys.argv) >= 3:
            manager.assign_game_image(sys.argv[2])
        elif cmd == 'assign-custom-image' and len(sys.argv) >= 4:
            manager.assign_game_image(sys.argv[2], sys.argv[3])
        elif cmd == 'backup':
            manager.backup_config()
        else:
            print("Usage: manage_gams.py [add|delete|duplicates|orphans|list|assign-image|assign-custom-image|backup] [args...]")
    else:
        manager.interactive_menu()

if __name__ == "__main__":
    main()
