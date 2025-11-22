#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AudioTensorBoard 命令行接口
"""

import sys
import argparse
from .app import create_app, find_event_file


def main():
    """主函数 - 命令行入口"""
    parser = argparse.ArgumentParser(
        prog='atb',
        description='AudioTensorBoard - 现代化的TensorBoard日志可视化工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 启动可视化服务器
  atb hifigan_logs/
  
  # 指定端口
  atb hifigan_logs/ --port 8080
  
  # 指定主机地址
  atb hifigan_logs/ --host 0.0.0.0 --port 8080
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
        help='服务器端口号 (默认: 6006)'
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
    print("\n" + "="*60)
    print("🚀 AudioTensorBoard 服务器已启动")
    print("="*60)
    print(f"📊 访问地址: http://{args.host}:{args.port}")
    print("💡 按 Ctrl+C 停止服务器")
    print("="*60 + "\n")
    
    # 启动服务器
    app.run(
        debug=args.debug,
        host=args.host,
        port=args.port
    )


if __name__ == '__main__':
    main()

