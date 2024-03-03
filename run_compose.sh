#!/bin/bash

# 切换到包含子目录的父目录
cd ~/VintageUser || exit

# 显示操作菜单
echo "请选择一个操作进行执行："
options=("restart" "down" "up -d" "pull" "stop")

select opt in "${options[@]}"
do
    case $opt in
        "restart")
            action="restart"
            break
            ;;
        "down")
            action="down"
            break
            ;;
        "up -d")
            action="up -d"
            break
            ;;
        "pull")
            action="pull"
            break
            ;;
        "stop")
            action="stop"
            break
            ;;
        *) echo "无效选项 $REPLY"; continue;;
    esac
done

# 遍历每个子目录执行选择的操作
for dir in */ ; do
    echo "Entering $dir"
    cd "$dir"
    
    # 检查compose.yaml文件是否存在
    if [ -f "compose.yaml" ]; then
        # 根据用户选择的操作执行 docker compose 命令
        echo "执行操作：docker compose -f compose.yaml $action"
        docker compose -f compose.yaml $action
    else
        echo "在 $dir 中没有找到 compose.yaml 文件"
    fi
    
    # 返回父目录
    cd ..
done

echo "操作完成。"