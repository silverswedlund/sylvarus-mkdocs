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
        # Use auto_link_strings if available, otherwise use name or key
        display_name = pantheon_key
        if "name" in pantheon_info:
            display_name = pantheon_info["name"]
        if "auto_link_strings" in pantheon_info and pantheon_info["auto_link_strings"]:
            display_name = pantheon_info["auto_link_strings"][0]
            
        description = pantheon_info.get("description", "")
        leader = pantheon_info.get("leader", "")
        members = pantheon_info.get("members", [])
        
        pantheons.append({
            "name": display_name,
            "key": pantheon_key,
            "description": description,
            "leader": leader,
            "members": members
        })
    
    # Sort pantheons alphabetically by name
    pantheons.sort(key=lambda x: x["name"])
    return pantheons

def get_pantheon_members(gods_json_path, pantheon_name, pantheon_auto_links):
    """Get all gods that belong to a specific pantheon."""
    data = load_json_data(gods_json_path)
    if not data:
        return []
    
    members = []
    for god_key, god_info in data.get("items", {}).items():
        god_pantheon = god_info.get("pantheon", "")
        
        # Check if the god's pantheon matches the pantheon name or any of its auto_link_strings
        if god_pantheon == pantheon_name or god_pantheon in pantheon_auto_links:
            # Use auto_link_strings if available, otherwise use name or key
            display_name = god_key
            if "name" in god_info:
                display_name = god_info["name"]
            if "auto_link_strings" in god_info and god_info["auto_link_strings"]:
                display_name = god_info["auto_link_strings"][0]
                
            members.append({
                "name": display_name,
                "key": god_key
            })
    
    # Sort members alphabetically by name
    members.sort(key=lambda x: x["name"])
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
        members = ", ".join([m for m in pantheon["members"]])
        
        # Use plain text without links
        table += f"| {name} | {description} | {leader} | {members} |\n"
    
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
        name = member["name"]
        table += f"| {name} | | |\n"
    
    return table

def update_pantheon_table(pantheons_json_path, table_insert_path, dry_run=False):
    """Update the pantheon table insert file."""
    try:
        # Get pantheon data
        pantheons = get_pantheon_data(pantheons_json_path)
        
        # Construct the markdown table
        table = construct_pantheon_markdown_table(pantheons)
        
        # Create parent directories if they don't exist
        if not dry_run:
            table_insert_path.parent.mkdir(parents=True, exist_ok=True)
        
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
            pantheon_key = pantheon["key"]
            pantheon_auto_links = pantheon.get("auto_link_strings", [])
            pantheon_dir = pantheon_key.lower().replace(" ", "").replace("'", "")
            
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
            members = get_pantheon_members(gods_json_path, pantheon_name, pantheon_auto_links)
            
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
    parser = argparse.ArgumentParser(description='Generate pantheon tables and write to insert files.')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    if args.dry_run:
        logging.info("🔍 DRY RUN: No files will be modified")
    
    # Paths to the files
    pantheons_json_path = Path("_json/pantheons_data.json")
    gods_json_path = Path("_json/entities/gods_data.json")
    table_insert_path = Path("docs/pantheons/pantheon_table.md_insert")
    pantheons_base_path = "docs/pantheons"
    
    # Update the pantheon table
    update_pantheon_table(pantheons_json_path, table_insert_path, args.dry_run)
    
    # Update member tables for each pantheon
    update_members_tables(pantheons_json_path, gods_json_path, pantheons_base_path, args.dry_run)

if __name__ == "__main__":
    main()
