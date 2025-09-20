#!/bin/bash

# Автоматическая диагностика сервера WorkerNet Portal
SERVER="10.0.21.221"
USER="worker"
PASSWORD="workernet"

echo "=== WORKERNET PORTAL AUTOMATIC DIAGNOSIS ==="
echo "Server: $SERVER"
echo "User: $USER"
echo ""

# Функция для выполнения команд на удаленном сервере
run_remote_command() {
    local cmd="$1"
    echo "Executing: $cmd"
    echo "----------------------------------------"
    
    # Используем expect для автоматического ввода пароля
    expect << EOF
spawn ssh $USER@$SERVER "$cmd"
expect "password:"
send "$PASSWORD\r"
expect eof
EOF
    echo ""
}

echo "1. Checking service status..."
run_remote_command "sudo systemctl status workernet-backend workernet-frontend --no-pager"

echo "2. Checking backend logs..."
run_remote_command "sudo journalctl -u workernet-backend --no-pager -n 10"

echo "3. Checking frontend logs..."
run_remote_command "sudo journalctl -u workernet-frontend --no-pager -n 10"

echo "4. Checking ports..."
run_remote_command "sudo netstat -tlnp | grep -E ':(3000|8000)'"

echo "5. Checking processes..."
run_remote_command "ps aux | grep -E '(python|node|webpack)' | grep -v grep"

echo "6. Checking service files..."
run_remote_command "ls -la /etc/systemd/system/workernet-*.service"

echo "=== DIAGNOSIS COMPLETE ==="
