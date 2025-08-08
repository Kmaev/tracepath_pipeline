#!/bin/bash

export PATH="/bin:/usr/bin:/usr/local/bin:$PATH"

# Get Python from REZ or system
python_bin=$(which python)

base_path="$PR_SHOW_ROOT/$PR_GROUP/$PR_ITEM/$PR_TASK"

# Validate environment
if [ -z "$PR_SHOW_ROOT" ] || [ -z "$PR_GROUP" ] || [ -z "$PR_ITEM" ] || [ -z "$PR_TASK" ]; then
    echo -e "${RED}One or more required environment variables are missing (PR_SHOW_ROOT, PR_GROUP, PR_ITEM, PR_TASK).${NC}"
    exit 1
fi

# Check if base path exists
if [ ! -d "$base_path" ]; then
    echo -e "${RED}Context not found: ${BOLD}$base_path${NC}"
    echo -e "${RED}To create a new item context, please contact support.${NC}"
    echo -e "${RED}Make sure the context you entered already exists.${NC}"
    exit 1
fi

# Call Python script with --dccs and passed arguments
"$python_bin" /Users/kmaev/Documents/hou_dev/tracepath_pipeline/modules/project_index/src/project_index/cli_create_subfolder.py \
    --dccs "$@"
