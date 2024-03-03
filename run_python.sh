#!/bin/bash

# 进入VintageUser目录
cd ~/VintageUser || exit

# 遍历每个子目录
for dir in */ ; do
  # 检查是否已经有针对该子目录的进程在运行
  if pgrep -f "python /root/VintageVigil/main.py -u $dir" > /dev/null; then
    echo "Process already running for $dir"
  else
    # 如果没有运行，则启动新的进程
    echo "Starting new process for $dir"
    nohup python /root/VintageVigil/main.py -u "$dir" &
  fi
done