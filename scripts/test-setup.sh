#!/bin/bash

# Comprehensive test script for the Docker setup
# This script tests all services and their connectivity

set -e

echo "🧪 Testing rrzz-rozbic-rzeczy-zrobione Docker Setup"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

test_service() {
    local service_name=$1
    local test_name=$2
    local test_command=$3
    
    echo -e "${BLUE}Testing ${service_name}: ${test_name}${NC}"
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "  ${RED}❌ FAIL${NC}"
        ((TESTS_FAILED++))
    fi
}

echo ""
echo "1. Docker Services Status"
echo "------------------------"

# Check if services are running
test_service "Docker Compose" "Services Running" "docker-compose ps | grep -q 'Up'"

# Check individual services
test_service "Neo4j" "Container Running" "docker-compose ps neo4j | grep -q 'Up'"
test_service "Ollama" "Container Running" "docker-compose ps ollama | grep -q 'Up'"
test_service "Backend" "Container Running" "docker-compose ps backend | grep -q 'Up'"
test_service "Frontend" "Container Running" "docker-compose ps frontend | grep -q 'Up'"

echo ""
echo "2. Service Health Checks"
echo "-----------------------"

# Test Neo4j connectivity
test_service "Neo4j" "HTTP API" "curl -f http://localhost:7474 > /dev/null 2>&1"
test_service "Neo4j" "Bolt Protocol" "docker-compose exec -T neo4j cypher-shell -u neo4j -p password 'RETURN 1;' > /dev/null 2>&1"

# Test Ollama connectivity
test_service "Ollama" "API Health" "curl -f http://localhost:11434/api/tags > /dev/null 2>&1"
test_service "Ollama" "Model Available" "curl -s http://localhost:11434/api/tags | grep -q 'qwen3:0.6b'"

# Test FastAPI backend
test_service "FastAPI" "Health Endpoint" "curl -f http://localhost:8000/health > /dev/null 2>&1"
test_service "FastAPI" "Response Format" "curl -s http://localhost:8000/health | grep -q 'status'"

# Test Streamlit frontend
test_service "Streamlit" "Web Interface" "curl -f http://localhost:8501 > /dev/null 2>&1"

echo ""
echo "3. Python Integration Tests"
echo "--------------------------"

# Test Ollama Python client
test_service "Ollama Client" "Python Import" "python -c 'from src.llm.ollama_client import OllamaLLM'"
test_service "Ollama Client" "Client Creation" "python -c 'from src.llm.ollama_client import OllamaLLM; client = OllamaLLM()'"
test_service "Ollama Client" "Health Check" "python -c 'from src.llm.ollama_client import OllamaLLM; client = OllamaLLM(); assert client.health_check()'"

echo ""
echo "4. Model Functionality"
echo "--------------------"

# Test text generation (if model is ready)
if curl -s http://localhost:11434/api/tags | grep -q 'qwen3:0.6b'; then
    test_service "Ollama Model" "Text Generation" "python -c 'from src.llm.ollama_client import OllamaLLM; client = OllamaLLM(); response = client.generate(\"Hello\"); assert len(response) > 0'"
else
    echo -e "${YELLOW}⚠️  Model not ready yet - skipping text generation test${NC}"
fi

echo ""
echo "5. Network Connectivity"
echo "----------------------"

# Test inter-service communication
test_service "Backend→Ollama" "Internal Network" "docker-compose exec backend curl -f http://ollama:11434/api/tags > /dev/null 2>&1"
test_service "Backend→Neo4j" "Internal Network" "docker-compose exec backend curl -f http://neo4j:7474 > /dev/null 2>&1"

echo ""
echo "6. Configuration Verification"
echo "----------------------------"

# Check environment variables
test_service "Environment" "OLLAMA_BASE_URL" "docker-compose exec backend env | grep -q 'OLLAMA_BASE_URL=http://ollama:11434'"
test_service "Environment" "NEO4J_URI" "docker-compose exec backend env | grep -q 'NEO4J_URI=bolt://neo4j:7687'"

echo ""
echo "📊 Test Results"
echo "=============="
echo -e "${GREEN}Tests Passed: ${TESTS_PASSED}${NC}"
echo -e "${RED}Tests Failed: ${TESTS_FAILED}${NC}"
echo -e "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All tests passed! Your setup is working correctly.${NC}"
    echo ""
    echo "📋 Available Services:"
    echo "  - FastAPI Backend: http://localhost:8000"
    echo "  - Neo4j Browser: http://localhost:7474 (user: neo4j, password: password)"
    echo "  - Streamlit Frontend: http://localhost:8501"
    echo "  - Ollama API: http://localhost:11434"
    echo ""
    echo "🚀 Next Steps:"
    echo "  1. Open http://localhost:8501 to use the Streamlit interface"
    echo "  2. Run: python examples/test_ollama.py for detailed Ollama testing"
    echo "  3. Start implementing note ingestion in src/backend/ingestion.py"
else
    echo ""
    echo -e "${RED}❌ Some tests failed. Check the output above for details.${NC}"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "  1. Check if all containers are running: docker-compose ps"
    echo "  2. View logs: docker-compose logs -f"
    echo "  3. Restart services: docker-compose restart"
    exit 1
fi 