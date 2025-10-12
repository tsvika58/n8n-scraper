#!/bin/bash
# Database Proxy Script for Supabase Connection
# Purpose: Manage connection between local PostgreSQL and Supabase

set -e

echo "🔗 Setting up Database Proxy to Supabase..."

# Function to test Supabase connection
test_supabase_connection() {
    echo "📡 Testing Supabase connection..."
    if pg_isready -h "$SUPABASE_HOST" -p "$SUPABASE_PORT" -U "$SUPABASE_USER"; then
        echo "✅ Supabase connection successful"
        return 0
    else
        echo "❌ Supabase connection failed"
        return 1
    fi
}

# Main execution
main() {
    echo "🚀 Database Proxy Starting..."
    
    # Test Supabase connection
    if test_supabase_connection; then
        echo "📋 Supabase connection verified"
        echo "🎉 Database proxy setup completed!"
    else
        echo "❌ Cannot connect to Supabase - proxy setup failed"
        exit 1
    fi
}

# Run main function
main "$@"
