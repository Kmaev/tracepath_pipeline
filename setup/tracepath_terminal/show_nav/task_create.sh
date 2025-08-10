#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Get Python from REZ env
python_bin=$(which python)

base_path="$PR_SHOW_ROOT/$PR_GROUP/$PR_ITEM"
task_path="$base_path/$PR_TASK"
context="$PR_SHOW/$PR_GROUP/$PR_ITEM"

# Validate environment
if [ -z "$PR_SHOW_ROOT" ] || [ -z "$PR_GROUP" ] || [ -z "$PR_ITEM" ]; then
    echo -e "${RED}One or more required environment variables are missing (PR_SHOW_ROOT, PR_GROUP, PR_ITEM).${NC}"
    exit 1
fi

# Check if base path exists
if [ ! -d "$base_path" ]; then
    echo -e "${RED}Context not found: ${BOLD}$context${NC}"
    echo -e "${RED}To create a new item context, please contact support.${NC}"
    echo -e "${RED}Make sure the context you entered already exists.${NC}"
    exit 1
fi

if [ ! -d "$task_path" ]; then
    echo -e "${YELLOW}Task is not found in: ${BOLD}$context${NC}"
    read -p "$(echo -e "${YELLOW}Would you like to create the task? (yes/no): ${NC}")" answer
    echo -e "${BOLD}=========================================================================${NC}"

    if [[ "$answer" =~ ^[Yy][Ee]?[Ss]?$ ]]; then
        read -p "$(echo -e "${YELLOW}Enter task name followed by space-separated DCC folder names: ${NC}")" -a user_input

        task_name="${user_input[0]}"
        dccs=("${user_input[@]:1}")

        if [[ -z "$task_name" || ${#dccs[@]} -eq 0 ]]; then
            echo -e "${RED}Task name or DCC list is empty.${NC}"
            exit 1
        fi

        "$python_bin" -m project_index.cli_create_task --name "$task_name" --dccs "${dccs[@]}"

    else
        echo -e "${BLUE}Cancelled. No task created.${NC}"
        exit 0
    fi
else
    echo -e "${BLUE}Task already exists: ${BOLD}$task_path${NC}"
fi
