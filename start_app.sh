#!/bin/bash

# 初始化 conda 环境
eval "$(conda shell.bash hook)"
conda activate kbot3

# 函数：启动服务并检查状态
start_service() {
    local service_name=$1
    local directory=$2
    local script=$3
    local wait_for_ready=$4
    local log_file="${LOG_DIR}/${service_name}_${TIMESTAMP}.log"
    
    echo "正在启动 ${service_name}..."
    
    # 切换到目录并启动服务（应用内已有日志管理）
    cd "$directory" && python "$script" &
    local pid=$!
    
    sleep 1
    if kill -0 $pid 2>/dev/null; then
        echo "✅ ${service_name} 已启动 (PID: $pid)"
        
        return 0
    else
        echo "❌ ${service_name} 启动失败！错误信息："
        cat "$log_file"
        return 1
    fi
}

# 启动主程序（并等待其完全启动）
start_service "文件摘要服务" "$(dirname "$0")" "main.py" "true" || exit 1

echo
echo "🎉 服务已成功启动！"
