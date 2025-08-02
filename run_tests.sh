#!/bin/bash
set -e

echo "🧪 Document Template Processing Service - Error Handling Test Suite"
echo "=================================================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if service is running
check_service() {
    local url=$1
    local name=$2
    echo -n "Checking $name... "
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${RED}✗ Not available${NC}"
        return 1
    fi
}

# Function to start services
start_services() {
    echo -e "${YELLOW}Starting services with Docker Compose...${NC}"
    docker compose up -d
    
    echo "Waiting for services to be ready..."
    sleep 10
    
    # Wait for services with retries
    for i in {1..12}; do
        if check_service "http://localhost:8000/" "Document Service" && \
           check_service "http://localhost:3000/" "Gotenberg Service"; then
            echo -e "${GREEN}✓ All services are ready${NC}"
            return 0
        fi
        echo "Waiting for services... (attempt $i/12)"
        sleep 5
    done
    
    echo -e "${RED}✗ Services failed to start properly${NC}"
    return 1
}

# Function to install test dependencies
install_dependencies() {
    echo -e "${YELLOW}Installing test dependencies...${NC}"
    
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements-test.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
}

# Function to run tests
run_tests() {
    echo -e "${YELLOW}Running comprehensive test suite...${NC}"
    
    source venv/bin/activate
    
    # Create test output directory
    mkdir -p test_results
    
    # Run tests with coverage and HTML report
    pytest test_error_handling.py \
        -v \
        --tb=short \
        --html=test_results/report.html \
        --self-contained-html \
        --cov=main \
        --cov-report=html:test_results/coverage \
        --cov-report=term-missing
    
    local test_exit_code=$?
    
    echo ""
    echo "Test Results:"
    echo "============="
    echo "HTML Report: test_results/report.html"
    echo "Coverage Report: test_results/coverage/index.html"
    
    return $test_exit_code
}

# Function to clean up
cleanup() {
    echo -e "${YELLOW}Cleaning up...${NC}"
    
    # Remove test files
    if [ -d "test_files" ]; then
        rm -rf test_files
        echo "✓ Removed test files"
    fi
    
    # Stop services
    docker compose down
    echo "✓ Stopped Docker services"
}

# Main execution
main() {
    local skip_services=false
    local cleanup_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-services)
                skip_services=true
                shift
                ;;
            --cleanup)
                cleanup_only=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --skip-services    Skip starting Docker services (assume already running)"
                echo "  --cleanup          Only cleanup test files and stop services"
                echo "  -h, --help         Show this help message"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use -h or --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Cleanup only mode
    if [ "$cleanup_only" = true ]; then
        cleanup
        exit 0
    fi
    
    # Check if we should start services
    if [ "$skip_services" = false ]; then
        # Check if services are already running
        if ! (check_service "http://localhost:8000/" "Document Service" && \
              check_service "http://localhost:3000/" "Gotenberg Service"); then
            start_services || {
                echo -e "${RED}Failed to start services${NC}"
                exit 1
            }
        else
            echo -e "${GREEN}✓ Services are already running${NC}"
        fi
    fi
    
    # Install dependencies and run tests
    install_dependencies || {
        echo -e "${RED}Failed to install dependencies${NC}"
        exit 1
    }
    
    run_tests
    local test_result=$?
    
    # Show final results
    echo ""
    if [ $test_result -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed!${NC}"
    else
        echo -e "${RED}❌ Some tests failed${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}To cleanup test environment:${NC}"
    echo "$0 --cleanup"
    
    exit $test_result
}

# Trap to ensure cleanup on script exit
trap 'echo -e "\n${YELLOW}Script interrupted${NC}"; exit 1' INT TERM

# Run main function
main "$@"