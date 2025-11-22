#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AudioTensorBoard 命令行接口
"""

import sys
import socket
import argparse
from .app import create_app, find_event_file


def is_port_available(host, port):
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False


def find_available_port(host, start_port, max_attempts=10):
    """查找可用端口"""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(host, port):
            return port
    return None


def main():
    """主函数 - 命令行入口"""
    parser = argparse.ArgumentParser(
        prog='atb',
        description='AudioTensorBoard - 现代化的TensorBoard日志可视化工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 启动可视化服务器（默认端口 6006，如被占用会自动切换）
  atb hifigan_logs/
  
  # 指定端口（如指定端口被占用则报错）
  atb hifigan_logs/ --port 8080
  
  # 指定主机地址和端口
  atb hifigan_logs/ --host 0.0.0.0 --port 8080
  
  # 指定主机地址为 0.0.0.0 以便外网访问（自动选择端口）
  atb hifigan_logs/ --host 0.0.0.0
        """
    )
    
    parser.add_argument(
        'logdir',
        help='TensorBoard事件文件路径或包含事件文件的目录'
    )
    
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='服务器主机地址 (默认: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=6006,
        help='服务器端口号 (默认: 6006，如被占用会自动寻找可用端口)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )
    
    args = parser.parse_args()
    
    # 检测用户是否手动指定了端口
    port_manually_specified = '--port' in sys.argv or '-p' in sys.argv
    
    # 查找事件文件
    event_file = find_event_file(args.logdir)
    
    if not event_file:
        print(f"❌ 错误: 在 {args.logdir} 中未找到事件文件", file=sys.stderr)
        sys.exit(1)
    
    print(f"📂 加载事件文件: {event_file}")
    
    # 创建Flask应用
    try:
        app = create_app(event_file)
    except Exception as e:
        print(f"❌ 错误: 无法加载事件文件: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("✅ 事件文件加载完成")
    
    # 检查端口可用性
    port = args.port
    if not is_port_available(args.host, port):
        if not port_manually_specified:
            # 默认端口被占用，自动寻找可用端口
            print(f"⚠️  默认端口 {port} 已被占用，正在自动查找可用端口...")
            available_port = find_available_port(args.host, port + 1)
            if available_port:
                port = available_port
                print(f"✅ 找到可用端口: {port}")
            else:
                print(f"❌ 错误: 无法找到可用端口 (尝试范围: {port + 1}-{port + 10})", file=sys.stderr)
                sys.exit(1)
        else:
            # 用户手动指定的端口被占用，报错退出
            print(f"❌ 错误: 指定的端口 {port} 已被占用", file=sys.stderr)
            print(f"💡 提示: 请选择其他端口，或不指定端口让程序自动选择", file=sys.stderr)
            sys.exit(1)
    
    print("\n" + "="*60)
    print("🚀 AudioTensorBoard 服务器已启动")
    print("="*60)
    print(f"📊 访问地址: http://{args.host}:{port}")
    print("💡 按 Ctrl+C 停止服务器")
    print("="*60 + "\n")
    
    # 启动服务器
    app.run(
        debug=args.debug,
        host=args.host,
        port=port
    )


if __name__ == '__main__':
    main()

