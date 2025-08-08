#!/bin/bash
# CoT Version Check Script
# Check for updates to Chain-of-Thought specification

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REGISTRY_URL="${COT_REGISTRY_URL:-https://cot-standard.org/registry.json}"
LOCAL_REGISTRY="$(dirname "$0")/registry.json"
SIMULATED_REGISTRY_URL="https://raw.githubusercontent.com/cot-standard/spec/main/registry.json"
CURRENT_VERSION="${1:-}"

# Function to check version
check_version() {
    echo "🔍 Checking CoT specification version..."
    
    # Fetch registry - try online first, then simulated, then local
    if command -v curl &> /dev/null; then
        # Try primary registry
        REGISTRY=$(curl -s "$REGISTRY_URL" 2>/dev/null)
        
        # If primary fails, try simulated live registry
        if [ -z "$REGISTRY" ]; then
            echo -e "${YELLOW}⚠ Primary registry unavailable, trying GitHub mirror...${NC}"
            REGISTRY=$(curl -s "$SIMULATED_REGISTRY_URL" 2>/dev/null)
            if [ -n "$REGISTRY" ]; then
                echo -e "${GREEN}✓ Retrieved from GitHub mirror${NC}"
            fi
        fi
        
        # Final fallback to local
        if [ -z "$REGISTRY" ] && [ -f "$LOCAL_REGISTRY" ]; then
            echo -e "${YELLOW}⚠ Cannot reach any online registry, using local copy${NC}"
            REGISTRY=$(cat "$LOCAL_REGISTRY")
        fi
    elif command -v wget &> /dev/null; then
        # Try primary registry
        REGISTRY=$(wget -qO- "$REGISTRY_URL" 2>/dev/null)
        
        # If primary fails, try simulated live registry
        if [ -z "$REGISTRY" ]; then
            echo -e "${YELLOW}⚠ Primary registry unavailable, trying GitHub mirror...${NC}"
            REGISTRY=$(wget -qO- "$SIMULATED_REGISTRY_URL" 2>/dev/null)
            if [ -n "$REGISTRY" ]; then
                echo -e "${GREEN}✓ Retrieved from GitHub mirror${NC}"
            fi
        fi
        
        # Final fallback to local
        if [ -z "$REGISTRY" ] && [ -f "$LOCAL_REGISTRY" ]; then
            echo -e "${YELLOW}⚠ Cannot reach any online registry, using local copy${NC}"
            REGISTRY=$(cat "$LOCAL_REGISTRY")
        fi
    elif [ -f "$LOCAL_REGISTRY" ]; then
        echo -e "${YELLOW}⚠ No curl/wget found, using local registry${NC}"
        REGISTRY=$(cat "$LOCAL_REGISTRY")
    else
        echo -e "${RED}Error: Neither curl nor wget found, and no local registry${NC}"
        exit 1
    fi
    
    # Parse latest version
    if command -v jq &> /dev/null; then
        LATEST_VERSION=$(echo "$REGISTRY" | jq -r .latest.version)
        LATEST_DATE=$(echo "$REGISTRY" | jq -r .latest.released)
    else
        # Fallback to Python
        LATEST_VERSION=$(echo "$REGISTRY" | python3 -c "import sys,json; print(json.load(sys.stdin)['latest']['version'])")
        LATEST_DATE=$(echo "$REGISTRY" | python3 -c "import sys,json; print(json.load(sys.stdin)['latest']['released'])")
    fi
    
    echo "Latest version: $LATEST_VERSION (released: $LATEST_DATE)"
    
    # Compare versions if current provided
    if [ -n "$CURRENT_VERSION" ]; then
        if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
            echo -e "${GREEN}✓ You are using the latest version${NC}"
        else
            echo -e "${YELLOW}⚠ Update available: $CURRENT_VERSION → $LATEST_VERSION${NC}"
            
            # Check if it's a breaking change
            MAJOR_CURRENT=$(echo "$CURRENT_VERSION" | cut -d. -f1)
            MAJOR_LATEST=$(echo "$LATEST_VERSION" | cut -d. -f1)
            
            if [ "$MAJOR_LATEST" -gt "$MAJOR_CURRENT" ]; then
                echo -e "${RED}⚠ This is a major version update with breaking changes${NC}"
                echo "See migration guide: https://cot-standard.org/migrate/v${MAJOR_CURRENT}-to-v${MAJOR_LATEST}"
            fi
        fi
    fi
}

# Function to show version details
show_details() {
    VERSION="${1:-$LATEST_VERSION}"
    echo ""
    echo "📋 Version $VERSION details:"
    
    if command -v jq &> /dev/null; then
        echo "$REGISTRY" | jq ".versions[] | select(.version == \"$VERSION\")"
    else
        echo "Install jq for detailed version information"
    fi
}

# Main execution
case "${1:-check}" in
    "check"|"")
        check_version "$2"
        ;;
    "details")
        check_version
        show_details "$2"
        ;;
    "all")
        check_version
        echo ""
        echo "📊 All versions:"
        if command -v jq &> /dev/null; then
            echo "$REGISTRY" | jq -r '.versions[] | "\(.version) - \(.stability) (released: \(.released))"'
        else
            echo "$REGISTRY" | python3 -c "import sys,json; versions=json.load(sys.stdin)['versions']; [print(f\"{v['version']} - {v['stability']} (released: {v['released']})\") for v in versions]"
        fi
        ;;
    "--help"|"-h")
        echo "CoT Version Check - Check for Chain-of-Thought specification updates"
        echo ""
        echo "Usage:"
        echo "  $0 [command] [version]"
        echo ""
        echo "Commands:"
        echo "  check [version]  - Check if version is latest (default)"
        echo "  details [version] - Show version details"
        echo "  all              - List all versions"
        echo ""
        echo "Examples:"
        echo "  $0                  # Check latest version"
        echo "  $0 check 6.0.0      # Check if 6.0.0 is latest"
        echo "  $0 details 7.0.0    # Show v7.0.0 details"
        echo "  $0 all              # List all versions"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac