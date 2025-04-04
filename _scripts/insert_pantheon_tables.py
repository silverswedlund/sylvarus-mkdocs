#!/usr/bin/env python3
import json
import logging
from pathlib import Path
import sys
import argparse
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def load_json_data(json_path):
    """Load data from a JSON file."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            logging.info(f"Loading data from {json_path}")
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load data from {json_path}: {e}")
        return None

def get_pantheon_data(json_path):
    """Get pantheon data from the JSON file."""
    data = load_json_data(json_path)
    if not data:
        return []
    
    pantheons = []
    for pantheon_key, pantheon_info in data.get("items", {}).items():
        name = pantheon_info.get("name", pantheon_key)
        description = pantheon_info.get("description", "")
        leader = pantheon_info.get("leader", "")
        members = pantheon_info.get("members", [])
        
        pantheons.append({
            "name": name,
            "description": description,
            "leader": leader,
            "members": members
        })
    
    # Sort pantheons alphabetically by name
    pantheons.sort(key=lambda x: x["name"])
    return pantheons

def get_pantheon_members(gods_json_path, pantheon_name):
    """Get all gods that belong to a specific pantheon."""
    data = load_json_data(gods_json_path)
    if not data:
        return []
    
    members = []
    for god_key, god_info in data.get("items", {}).items():
        if god_info.get("pantheon") == pantheon_name:
            name = god_info.get("name", god_key)
            members.append(name)
    
    # Sort members alphabetically
    members.sort()
    return members

def construct_pantheon_markdown_table(pantheons):
    """Construct a markdown table for pantheons."""
    if not pantheons:
        return "No pantheons found."
    
    # Create table header
    table = "| Pantheon | Description | Leader | Members |\n"
    table += "|----------|-------------|--------|--------|\n"
    
    # Add rows for each pantheon
    for pantheon in pantheons:
        name = pantheon["name"]
        description = pantheon["description"]
        leader = pantheon["leader"]
        members = ", ".join(pantheon["members"])
        
        # Create links for pantheon names
        pantheon_path = name.lower().replace(" ", "").replace("'", "")
        name_link = f"[{name}](pantheons/{pantheon_path}/index.md)"
        
        table += f"| {name_link} | {description} | {leader} | {members} |\n"
    
    return table

def construct_members_markdown_table(members, pantheon_name):
    """Construct a markdown table for pantheon members."""
    if not members:
        return "No members found for this pantheon."
    
    # Add a title to the table
    table = f"### Members of {pantheon_name}\n\n"
    
    # Create table header
    table += "| God | Role | Status |\n"
    table += "|-----|------|--------|\n"
    
    # Add rows for each member
    for member in members:
        # Create links for god names
        god_path = member.lower().replace(" ", "").replace("'", "").replace("(", "").replace(")", "")
        if "^" in god_path:
            god_path, _ = god_path.split("^", 1)
        name_link = f"[{member}](../../entities/gods/{god_path}/index.md)"
        
        # For now, leave role and status empty - these could be populated from god data
        table += f"| {name_link} | | |\n"
    
    return table

def update_pantheon_table(pantheons_json_path, table_insert_path, dry_run=False):
    """Update the pantheon table insert file."""
    try:
        # Get pantheon data
        pantheons = get_pantheon_data(pantheons_json_path)
        
        # Construct the markdown table
        table = construct_pantheon_markdown_table(pantheons)
        
        # Write to the insert file
        if not dry_run:
            with open(table_insert_path, "w", encoding="utf-8") as f:
                f.write(table)
            logging.info(f"✅ Updated pantheon table in {table_insert_path}")
        else:
            logging.info(f"🔍 Would update pantheon table in {table_insert_path}")
            logging.info(f"Table content would be:\n{table}")
            
    except Exception as e:
        logging.error(f"Failed to update pantheon table: {e}")
        sys.exit(1)

def update_members_tables(pantheons_json_path, gods_json_path, base_path, dry_run=False):
    """Update member tables for each pantheon."""
    try:
        # Get pantheon data
        pantheons = get_pantheon_data(pantheons_json_path)
        
        for pantheon in pantheons:
            pantheon_name = pantheon["name"]
            pantheon_dir = pantheon_name.lower().replace(" ", "").replace("'", "")
            
            # Create the pantheon directory if it doesn't exist
            pantheon_path = Path(base_path) / pantheon_dir
            # Ensure parent directories exist
            if not dry_run and not pantheon_path.parent.exists():
                os.makedirs(pantheon_path.parent, exist_ok=True)
                logging.info(f"Created parent directory: {pantheon_path.parent}")
            
            if not dry_run and not pantheon_path.exists():
                os.makedirs(pantheon_path, exist_ok=True)
                logging.info(f"Created directory for {pantheon_name}: {pantheon_path}")
            
            # Get members for this pantheon
            members = get_pantheon_members(gods_json_path, pantheon_name)
            
            # Construct the members table
            table = construct_members_markdown_table(members, pantheon_name)
            
            # Path to the members table insert file
            members_table_path = pantheon_path / "members_table.md_insert"
            
            # Write to the insert file
            if not dry_run:
                with open(members_table_path, "w", encoding="utf-8") as f:
                    f.write(table)
                logging.info(f"✅ Updated members table for {pantheon_name}")
            else:
                logging.info(f"🔍 Would update members table for {pantheon_name}")
                logging.info(f"Table content would be:\n{table}")
            
    except Exception as e:
        logging.error(f"Failed to update members tables: {e}")
        sys.exit(1)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Update pantheon table in the pantheon disambiguation file.')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    if args.dry_run:
        logging.info("🔍 DRY RUN: No files will be modified")
    
    # Paths to the files
    pantheons_json_path = Path("_json/pantheons_data.json")
    gods_json_path = Path("_json/gods_data.json")
    table_insert_path = Path("docs/pantheons/pantheon_table.md_insert")
    pantheons_base_path = "docs/pantheons"
    
    # Update the pantheon table
    update_pantheon_table(pantheons_json_path, table_insert_path, args.dry_run)
    
    # Update member tables for each pantheon
    update_members_tables(pantheons_json_path, gods_json_path, pantheons_base_path, args.dry_run)

if __name__ == "__main__":
    main()
