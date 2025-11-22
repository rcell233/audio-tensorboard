#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TensorBoard 可视化 Web 应用
使用 Flask + Jinja2 + Tailwind CSS
"""

import os
import base64
import threading
import time
from flask import Flask, render_template, jsonify
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

# 全局变量存储EventAccumulator
event_acc = None
log_dir = None
reload_thread = None
stop_reload = threading.Event()


def reload_worker(interval=10):
    """后台线程：定期重新加载TensorBoard日志
    
    Args:
        interval: 刷新间隔（秒），默认10秒
    """
    global event_acc
    print(f"🔄 自动刷新已启用：每 {interval} 秒增量检查新日志")
    
    while not stop_reload.is_set():
        # 等待指定的间隔时间，但允许被中断
        if stop_reload.wait(interval):
            break
        
        try:
            if event_acc is not None:
                print(f"🔄 正在重新加载日志... (增量更新)")
                start_time = time.time()
                event_acc.Reload()
                elapsed = time.time() - start_time
                print(f"✅ 日志重新加载完成 (耗时: {elapsed:.2f}秒)")
        except Exception as e:
            print(f"⚠️ 重新加载日志时出错: {e}")


def create_app(event_file_path, reload_interval=10):
    """创建Flask应用实例
    
    Args:
        event_file_path: TensorBoard事件文件路径
        reload_interval: 自动刷新间隔（秒），默认10秒
    """
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
    
    # 初始化EventAccumulator
    init_event_accumulator(event_file_path)
    
    # 启动后台刷新线程
    start_reload_thread(interval=reload_interval)
    
    @app.route('/')
    def index():
        """主页"""
        if event_acc is None:
            return "请先初始化EventAccumulator", 500
        
        tags = event_acc.Tags()
        
        return render_template('index.html',
                             scalar_tags=sorted(tags['scalars']),
                             image_tags=sorted(tags['images']),
                             audio_tags=sorted(tags['audio']),
                             file_version=event_acc.file_version)

    @app.route('/api/scalars/<path:tag>')
    def api_scalars(tag):
        """API: 获取标量数据"""
        try:
            events = event_acc.Scalars(tag)
            data = {
                'steps': [e.step for e in events],
                'values': [e.value for e in events],
                'wall_times': [e.wall_time for e in events]
            }
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/images/<path:tag>')
    def api_images(tag):
        """API: 获取图像数据"""
        try:
            events = event_acc.Images(tag)
            images = []
            for e in events:
                img_b64 = base64.b64encode(e.encoded_image_string).decode('utf-8')
                images.append({
                    'step': e.step,
                    'wall_time': e.wall_time,
                    'width': e.width,
                    'height': e.height,
                    'data': f'data:image/png;base64,{img_b64}'
                })
            return jsonify(images)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/audio/<path:tag>')
    def api_audio(tag):
        """API: 获取音频数据"""
        try:
            events = event_acc.Audio(tag)
            audios = []
            for e in events:
                audio_b64 = base64.b64encode(e.encoded_audio_string).decode('utf-8')
                audios.append({
                    'step': e.step,
                    'wall_time': e.wall_time,
                    'sample_rate': e.sample_rate,
                    'length_frames': e.length_frames,
                    'content_type': e.content_type,
                    'data': f'data:{e.content_type};base64,{audio_b64}'
                })
            return jsonify(audios)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app


def init_event_accumulator(path):
    """初始化EventAccumulator"""
    global event_acc, log_dir
    log_dir = path
    event_acc = EventAccumulator(path)
    event_acc.Reload()


def start_reload_thread(interval=10):
    """启动后台刷新线程
    
    Args:
        interval: 刷新间隔（秒），默认10秒
    """
    global reload_thread
    if reload_thread is None or not reload_thread.is_alive():
        stop_reload.clear()
        reload_thread = threading.Thread(
            target=reload_worker, 
            args=(interval,),
            daemon=True,
            name="LogReloadThread"
        )
        reload_thread.start()


def stop_reload_thread():
    """停止后台刷新线程"""
    global reload_thread
    if reload_thread is not None and reload_thread.is_alive():
        print("🛑 正在停止自动刷新线程...")
        stop_reload.set()
        reload_thread.join(timeout=5)
        print("✅ 自动刷新线程已停止")


def find_event_file(directory):
    """查找事件文件"""
    if os.path.isfile(directory):
        return directory
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if 'tfevents' in file and not file.endswith('.profile-empty'):
                return os.path.join(root, file)
    return None

