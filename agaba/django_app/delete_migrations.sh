#!/bin/bash
# TO RUN SCRIPT (bash!):
# bash delete_migrations.sh

# Navigate to the project root directory
cd /path/to/your/django/project

# Ask for confirmation
read -p "Are you sure you want to delete all old migrations? This cannot be undone! (y/n): " confirm

if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    # Find and delete all migration files except __init__.py
    find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
    find . -path "*/migrations/*.pyc" -delete

    echo "Old migrations deleted."
else
    echo "Deletion canceled."
fi