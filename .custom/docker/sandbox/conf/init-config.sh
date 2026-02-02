#!/bin/sh
# [CUSTOM] Sandbox 配置初始化脚本
# 功能: 根据 CPU 架构自动选择 syscall 白名单
# 位置: .custom/docker/sandbox/conf/ (符合二开规范)
# 使用: 在 sandbox 容器启动前执行

set -e

# 二开配置目录 (只读挂载)
CUSTOM_CONF_DIR="/custom-conf"
# 官方配置目录 (可写)
CONF_DIR="/conf"
ARCH=$(uname -m)

echo "[CUSTOM] Sandbox initialization starting..."
echo "[CUSTOM] Detected architecture: $ARCH"

# 选择架构特定的 syscall 配置
case "$ARCH" in
    aarch64|arm64)
        SYSCALL_FILE="$CUSTOM_CONF_DIR/arch/syscalls.aarch64.yaml"
        echo "[CUSTOM] Using ARM64 syscall whitelist"
        ;;
    x86_64|amd64)
        SYSCALL_FILE="$CUSTOM_CONF_DIR/arch/syscalls.x86_64.yaml"
        echo "[CUSTOM] Using x86_64 syscall whitelist"
        ;;
    *)
        echo "[CUSTOM] Warning: Unknown architecture $ARCH, using default config"
        SYSCALL_FILE=""
        ;;
esac

# 如果有架构特定配置，合并到 config.yaml
if [ -n "$SYSCALL_FILE" ] && [ -f "$SYSCALL_FILE" ]; then
    if [ -f "$CUSTOM_CONF_DIR/config.base.yaml" ]; then
        # 合并: 基础配置 + 架构特定 syscall
        cat "$CUSTOM_CONF_DIR/config.base.yaml" > "$CONF_DIR/config.yaml"
        echo "" >> "$CONF_DIR/config.yaml"
        cat "$SYSCALL_FILE" >> "$CONF_DIR/config.yaml"
        echo "[CUSTOM] Config merged: config.base.yaml + $(basename $SYSCALL_FILE)"
    else
        echo "[CUSTOM] Warning: config.base.yaml not found in $CUSTOM_CONF_DIR"
        echo "[CUSTOM] Using existing config.yaml"
    fi
else
    echo "[CUSTOM] Using existing config.yaml (no architecture-specific config)"
fi

# 创建必要目录并设置权限
mkdir -p /var/sandbox/sandbox-python/tmp /tmp
chmod 777 /var/sandbox/sandbox-python/tmp /tmp
echo "[CUSTOM] Temporary directories created with proper permissions"

echo "[CUSTOM] Sandbox initialization complete"
echo "[CUSTOM] Starting sandbox..."

# 启动 sandbox
exec /main
