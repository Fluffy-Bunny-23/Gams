#!/usr/bin/env python3
"""
Gams Game Adder CLI Tool
Automatically adds games from UGS (Universal Game Site) to Gams collection.
"""

import os
import sys
import re
import json
import requests
import time
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Dict, Optional, Tuple

class GamsGameAdder:
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
            import shutil
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
        print(f"\n🎮 Adding game: {game_id}")
        
        # Get readable name
        game_name = self.get_game_name(game_id)
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
            img_path = self.create_game_image(game_name)
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
    
    def interactive_add(self):
        """Interactive mode for adding games."""
        print("🎮 Gams Game Adder - Interactive Mode")
        print("=" * 50)
        
        # Load games
        games = self.load_ugs_games()
        if not games:
            print("✗ Could not load games from UGS")
            return
        
        while True:
            print("\n📝 Options:")
            print("1. Search for a game")
            print("2. Browse by letter")
            print("3. List recent additions")
            print("4. Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                self.search_and_add()
            elif choice == '2':
                self.browse_by_letter()
            elif choice == '3':
                self.list_recent_games()
            elif choice == '4':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option")
    
    def search_and_add(self):
        """Search for games and add selected one."""
        query = input("🔍 Enter search term: ").strip()
        if not query:
            return
        
        matches = self.search_games(query)
        
        if not matches:
            print("❌ No games found")
            return
        
        print(f"\n📋 Found {len(matches)} games:")
        for i, game in enumerate(matches[:10], 1):  # Show first 10
            name = self.get_game_name(game)
            print(f"{i:2d}. {name}")
        
        if len(matches) > 10:
            print(f"... and {len(matches) - 10} more")
        
        try:
            selection = input(f"\nSelect game (1-{min(10, len(matches))}): ").strip()
            idx = int(selection) - 1
            
            if 0 <= idx < min(10, len(matches)):
                selected_game = matches[idx]
                self.process_game_selection(selected_game)
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Invalid input")
    
    def browse_by_letter(self):
        """Browse games by first letter."""
        games = self.load_ugs_games()
        
        # Get unique first letters
        letters = sorted(set(
            game[2:3].upper() if game.startswith('cl') and len(game) > 2 else 'A'
            for game in games
        ))
        
        print(f"\n📚 Available letters: {' '.join(letters)}")
        letter = input("🔤 Enter letter: ").strip().upper()
        
        if letter not in letters:
            print("❌ Invalid letter")
            return
        
        # Filter games by letter
        filtered = [
            game for game in games 
            if game.startswith('cl') and len(game) > 2 and game[2:3].upper() == letter
        ]
        
        print(f"\n📋 Games starting with '{letter}':")
        for i, game in enumerate(filtered[:10], 1):
            name = self.get_game_name(game)
            print(f"{i:2d}. {name}")
        
        if len(filtered) > 10:
            print(f"... and {len(filtered) - 10} more")
        
        try:
            selection = input(f"\nSelect game (1-{min(10, len(filtered))}): ").strip()
            idx = int(selection) - 1
            
            if 0 <= idx < min(10, len(filtered)):
                selected_game = filtered[idx]
                self.process_game_selection(selected_game)
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Invalid input")
    
    def process_game_selection(self, game_id: str):
        """Process selected game and add to Gams."""
        game_name = self.get_game_name(game_id)
        
        print(f"\n🎮 Selected: {game_name}")
        print("📂 Available sections:")
        for i, section in enumerate(self.sections, 1):
            print(f"{i}. {section}")
        
        try:
            section_choice = input(f"Select section (1-{len(self.sections)}): ").strip()
            idx = int(section_choice) - 1
            
            if 0 <= idx < len(self.sections):
                section = self.sections[idx]
                
                # Ask about custom image
                custom_img = input("Use custom image? (y/N): ").strip().lower()
                use_custom = custom_img.startswith('y')
                
                # Add the game
                self.add_game(game_id, section, use_custom)
            else:
                print("❌ Invalid section")
        except ValueError:
            print("❌ Invalid input")
    
    def list_recent_games(self):
        """List recently added games."""
        print("\n📜 Recent additions to Gams:")
        print("(This would show recently added games)")
        print("Feature not yet implemented")

def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Command line mode
        adder = GamsGameAdder()
        
        if sys.argv[1] == "add" and len(sys.argv) >= 3:
            game_id = sys.argv[2]
            section = sys.argv[3] if len(sys.argv) > 3 else "Custom"
            use_custom_img = "--custom-img" in sys.argv
            
            adder.add_game(game_id, section, use_custom_img)
        elif sys.argv[1] == "search" and len(sys.argv) >= 3:
            query = sys.argv[2]
            matches = adder.search_games(query)
            for game in matches[:10]:
                print(f"{game} -> {adder.get_game_name(game)}")
        elif sys.argv[1] == "help":
            print("Gams Game Adder CLI")
            print("Usage:")
            print("  python gams_adder.py add <game_id> [section] [--custom-img]")
            print("  python gams_adder.py search <query>")
            print("  python gams_adder.py              # Interactive mode")
        else:
            print("Unknown command. Use 'help' for usage.")
    else:
        # Interactive mode
        adder = GamsGameAdder()
        adder.interactive_add()

if __name__ == "__main__":
    main()