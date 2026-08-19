#!/bin/bash
# SLFN Business OS - Automated Rollback Script
# Usage: ./scripts/rollback.sh [tag_name]
# If no tag provided, lists available rollback points

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# List rollback tags
list_rollbacks() {
    print_info "Available rollback points:"
    git tag -l "rollback-pre-*" | sort -r | while read tag; do
        # Get tag date and commit message
        tag_date=$(git log -1 --format="%ci" "$tag" 2>/dev/null || echo "unknown")
        commit_msg=$(git log -1 --format="%s" "$tag" 2>/dev/null || echo "unknown")
        echo "  $tag  ($tag_date)  $commit_msg"
    done
}

# Create rollback tag
create_rollback() {
    local tag_name="rollback-pre-$(date +%Y%m%d-%H%M%S)"
    print_step "Creating rollback tag: $tag_name"
    git tag "$tag_name" HEAD
    print_info "Rollback tag created: $tag_name"
    echo "$tag_name"
}

# Rollback to specific tag
rollback_to() {
    local target_tag="$1"
    
    if [ -z "$target_tag" ]; then
        print_error "No tag specified. Use --list to see available tags."
        exit 1
    fi
    
    # Verify tag exists
    if ! git rev-parse "$target_tag" >/dev/null 2>&1; then
        print_error "Tag '$target_tag' does not exist"
        list_rollbacks
        exit 1
    fi
    
    print_warning "This will HARD RESET to $target_tag"
    print_warning "ALL UNCOMMITTED CHANGES WILL BE LOST"
    read -p "Continue? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        print_info "Rollback cancelled"
        exit 0
    fi
    
    print_step "Rolling back to $target_tag..."
    git reset --hard "$target_tag"
    print_info "Rollback complete. Current HEAD: $(git rev-parse --short HEAD)"
    
    # Offer to delete the tag
    read -p "Delete rollback tag $target_tag? (yes/no): " delete_tag
    if [ "$delete_tag" = "yes" ]; then
        git tag -d "$target_tag"
        print_info "Rollback tag deleted"
    fi
}

# Soft rollback (keeps changes)
soft_rollback_to() {
    local target_tag="$1"
    
    if [ -z "$target_tag" ]; then
        print_error "No tag specified"
        exit 1
    fi
    
    if ! git rev-parse "$target_tag" >/dev/null 2>&1; then
        print_error "Tag '$target_tag' does not exist"
        exit 1
    fi
    
    print_step "Soft rolling back to $target_tag (changes kept)..."
    git reset --soft "$target_tag"
    print_info "Soft rollback complete. Changes are now unstaged."
}

# Main
case "${1:-}" in
    --list|-l)
        list_rollbacks
        ;;
    --create|-c)
        create_rollback
        ;;
    --soft|-s)
        soft_rollback_to "$2"
        ;;
    --help|-h)
        echo "Usage: $0 [options] [tag]"
        echo ""
        echo "Options:"
        echo "  --list, -l       List available rollback points"
        echo "  --create, -c     Create new rollback tag at HEAD"
        echo "  --soft, -s TAG   Soft rollback to TAG (keeps changes)"
        echo "  --help, -h       Show this help"
        echo ""
        echo "Without options: Hard rollback to specified TAG"
        echo "  $0 rollback-pre-20260819-143022"
        ;;
    *)
        if [ -z "$1" ]; then
            list_rollbacks
        else
            rollback_to "$1"
        fi
        ;;
esac