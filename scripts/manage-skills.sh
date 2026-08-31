#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_DIR="${SKILLS_SOURCE_DIR:-$REPO_ROOT/skills}"
TARGET_DIR="${SKILLS_TARGET_DIR:-$PWD/.agents/skills}"

usage() {
    echo "Usage:"
    echo "  $0 list                     # list skills by name"
    echo "  $0 install <name|number>    # symlink one skill into the target repo"
    echo "  $0 install-all              # symlink every skill"
    echo "  $0 uninstall <name>         # remove a skill symlink"
    echo "  $0 doctor                   # validate the library (skills-doctor.py)"
    echo ""
    echo "Skills come from $REPO_ROOT/skills and are linked into the current"
    echo "directory's .agents/skills. Override with SKILLS_SOURCE_DIR / SKILLS_TARGET_DIR."
}

SORTED_SKILLS=()

load_sorted_skills() {
    if [[ ! -d "$SOURCE_DIR" ]]; then
        echo "Error: Skills source directory not found: $SOURCE_DIR" >&2
        exit 1
    fi

    mapfile -t SORTED_SKILLS < <(find "$SOURCE_DIR" -mindepth 1 -maxdepth 1 -type d -not -name '.*' -printf '%f\n' | LC_ALL=C sort)
}

list_skills() {
    local i

    load_sorted_skills

    for i in "${!SORTED_SKILLS[@]}"; do
        printf "%d. %s\n" "$((i + 1))" "${SORTED_SKILLS[$i]}"
    done
}

resolve_skill_name() {
    # Accepts a skill name (preferred, stable) or a 1-based list number (legacy).
    local selector="$1"
    local candidate

    load_sorted_skills

    for candidate in "${SORTED_SKILLS[@]}"; do
        if [[ "$candidate" == "$selector" ]]; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done

    if [[ "$selector" =~ ^[0-9]+$ ]] && (( 10#$selector >= 1 )) && (( 10#$selector <= ${#SORTED_SKILLS[@]} )); then
        echo "Note: numeric install is positional and changes when skills are added/removed; prefer the name." >&2
        printf '%s\n' "${SORTED_SKILLS[$((10#$selector - 1))]}"
        return 0
    fi

    echo "Error: No skill named '$selector'. Run '$0 list' to see available skills." >&2
    return 1
}

install_skill() {
    local selector="${1:-}"
    local skill_name

    if [[ -z "$selector" ]]; then
        echo "Error: Missing skill name for install" >&2
        usage
        exit 1
    fi

    skill_name="$(resolve_skill_name "$selector")" || exit 1
    link_skill_to_target "$skill_name" "$SOURCE_DIR/$skill_name" "$TARGET_DIR"
}

install_all_skills() {
    local skill_name

    load_sorted_skills
    for skill_name in "${SORTED_SKILLS[@]}"; do
        link_skill_to_target "$skill_name" "$SOURCE_DIR/$skill_name" "$TARGET_DIR"
    done
}

uninstall_skill() {
    local skill_name="${1:-}"
    local target_path

    if [[ -z "$skill_name" ]]; then
        echo "Error: Missing skill name for uninstall" >&2
        usage
        exit 1
    fi

    target_path="$TARGET_DIR/$skill_name"

    if [[ -L "$target_path" ]]; then
        rm "$target_path"
        echo "Removed: $target_path"
    elif [[ -e "$target_path" ]]; then
        echo "Error: $target_path exists but is not a symlink; refusing to remove" >&2
        exit 1
    else
        echo "Not installed: $skill_name"
    fi
}

run_doctor() {
    python3 "$SCRIPT_DIR/skills-doctor.py" "$SOURCE_DIR"
}

link_skill_to_target() {
    local skill_name="$1"
    local source_path="$2"
    local base_target_dir="$3"
    local target_path="$base_target_dir/$skill_name"
    local source_realpath
    local target_realpath

    mkdir -p "$base_target_dir"
    source_realpath="$(readlink -f "$source_path")"

    if [[ -L "$target_path" ]]; then
        target_realpath="$(readlink -f "$target_path" || true)"

        if [[ "$target_realpath" == "$source_realpath" ]]; then
            echo "Already linked: $target_path"
            return
        fi

        rm "$target_path"
    elif [[ -e "$target_path" ]]; then
        echo "Error: Target already exists and is not a symlink: $target_path" >&2
        exit 1
    fi

    ln -s "$source_path" "$target_path"
    echo "Linked: $target_path -> $source_path"
}

command="${1:-list}"

case "$command" in
    list)
        list_skills
        ;;
    install)
        install_skill "${2:-}"
        ;;
    install-all)
        install_all_skills
        ;;
    uninstall)
        uninstall_skill "${2:-}"
        ;;
    doctor)
        run_doctor
        ;;
    *)
        echo "Error: Unknown command '$command'" >&2
        usage
        exit 1
        ;;
esac
