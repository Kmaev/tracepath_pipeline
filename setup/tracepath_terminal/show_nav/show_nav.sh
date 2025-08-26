GREEN='\033[38;5;34m'
RESET='\033[0m'  # reset back to normal

TASK_CREATE_SH="$TRACEPATH_SHELL_ROOT/task_create.sh"
SUBFOLDERS_SH="$TRACEPATH_SHELL_ROOT/subfolders_create.sh"

load() {
    export PR_SHOW="$1"
    export PR_SHOW_ROOT="$PR_PROJECTS_PATH/$PR_SHOW"
    echo -e "${GREEN}[INFO] Active project: $PR_SHOW${RESET}"
}

cdtask() {
    export PR_GROUP="$1"
    export PR_ITEM="$2"
    export PR_TASK="$3"
    local path="$PR_SHOW_ROOT/$PR_GROUP/$PR_ITEM/$PR_TASK"

    if [[ -d "$path" ]]; then
        cd "$path" || {
            echo "[ERROR] Failed to change directory to: $path"

            return 1
        }
        show_context
        #echo "[INFO] Moved to: $path"
    else
        echo "[ERROR] Task does not exist: $path"
        echo "========================================================================="
        "$TASK_CREATE_SH" "$PR_TASK" "$@"
        cd "$path" || return 1
    fi
}

add() {
    local path="$PR_SHOW_ROOT/$PR_GROUP/$PR_ITEM/$PR_TASK"
    if [[ ! -d "$path" ]]; then
        echo "[ERROR] Context does not exist: $path"
        return 1
    fi
    cd "$path" || {
        echo "[ERROR] Failed to change directory to: $path"
        return 1
    }
    cd "$path" || return 1
    "$SUBFOLDERS_SH" "$@"
    }

show_context() {
    local show=${PR_SHOW:-None}
    local group=${PR_GROUP:-None}
    local item=${PR_ITEM:-None}
    local task=${PR_TASK:-None}

    echo -e "${GREEN}[INFO] Project: $show${RESET} || ${GREEN}Group: $group${RESET} || ${GREEN}Item: $item${RESET} || ${GREEN}Task: $task${RESET}"
}






