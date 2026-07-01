#!/bin/bash

# Configuration
LOG_FILE="test_report_$(date +%Y%m%d_%H%M%S).log"
touch "$LOG_FILE"

# Function to log messages to both console and file
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Function to run a command and log its output
run_test() {
    local test_name="$1"
    local command="$2"
    
    log "\n========================================================"
    log "🚀 RUNNING TEST: $test_name"
    log "========================================================"
    
    # Run the command, append both stdout and stderr to the log
    if eval "$command" >> "$LOG_FILE" 2>&1; then
        log "✅ PASSED: $test_name"
        return 0
    else
        log "❌ FAILED: $test_name. Check the log above for details."
        return 1
    fi
}

log "Starting comprehensive system test at $(date)"
log "Full results will be saved to: $LOG_FILE"
echo ""

FAILURES=0

# 1. Run Backend Tests
log "⏳ 1. Testing Backend (Pytest)..."
run_test "Backend Unit & Integration Tests" "(cd backend && source .venv/bin/activate && PYTHONPATH=. pytest -v)" || FAILURES=$((FAILURES+1))

# 2. Run Frontend Tests
log "⏳ 2. Testing Frontend (Vitest)..."
run_test "Frontend Component Tests" "(cd frontend && npx vitest run)" || FAILURES=$((FAILURES+1))

# 3. Check Live Services (if Docker is running)
log "\n⏳ 3. Checking Live Services (Docker)..."
if docker compose ps | grep -q "Up"; then
    log "Docker containers detected. Running health checks..."
    
    # Check Database
    run_test "Database Container Running" "docker compose ps | grep mysql | grep -q 'Up'" || FAILURES=$((FAILURES+1))
    
    # Check Backend API
    run_test "Backend API Responding" "curl -s -f -o /dev/null http://localhost:8000/docs" || FAILURES=$((FAILURES+1))
    
    # Check Frontend UI
    run_test "Frontend UI Responding" "curl -s -f -o /dev/null http://localhost:3000" || FAILURES=$((FAILURES+1))
else
    log "⚠️  Docker containers are not currently running. Skipping live service health checks."
    log "   (Run './start.sh' to start them if you want to test live endpoints)."
fi

# Final Summary
log "\n========================================================"
log "🏁 TEST SUITE COMPLETED"
log "========================================================"
if [ "$FAILURES" -eq 0 ]; then
    log "🎉 ALL TESTS PASSED SUCCESSFULLY!"
else
    log "🚨 $FAILURES TEST(S) FAILED. Please review the log file: $LOG_FILE"
fi

exit $FAILURES
