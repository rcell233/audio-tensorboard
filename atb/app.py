#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TensorBoard 可视化 Web 应用
使用 Flask + Jinja2 + Tailwind CSS
"""

import os
import base64
from flask import Flask, render_template, jsonify
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

# 全局变量存储EventAccumulator
event_acc = None
log_dir = None


def create_app(event_file_path):
    """创建Flask应用实例"""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
    
    # 初始化EventAccumulator
    init_event_accumulator(event_file_path)
    
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


def find_event_file(directory):
    """查找事件文件"""
    if os.path.isfile(directory):
        return directory
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if 'tfevents' in file and not file.endswith('.profile-empty'):
                return os.path.join(root, file)
    return None

