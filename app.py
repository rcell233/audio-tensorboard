#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TensorBoard 可视化 Web 应用
使用 Flask + Jinja2 + Tailwind CSS
"""

import os
import base64
import io
from flask import Flask, render_template, jsonify, send_file
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

app = Flask(__name__)

# 全局变量存储EventAccumulator
event_acc = None
log_dir = None


def init_event_accumulator(path):
    """初始化EventAccumulator"""
    global event_acc, log_dir
    log_dir = path
    event_acc = EventAccumulator(path)
    event_acc.Reload()


def get_scalar_data(tag):
    """获取标量数据"""
    events = event_acc.Scalars(tag)
    return {
        'steps': [e.step for e in events],
        'values': [e.value for e in events],
        'wall_times': [e.wall_time for e in events]
    }


def get_image_data(tag):
    """获取图像数据"""
    events = event_acc.Images(tag)
    images = []
    for e in events:
        # 将图像编码为base64
        img_b64 = base64.b64encode(e.encoded_image_string).decode('utf-8')
        images.append({
            'step': e.step,
            'wall_time': e.wall_time,
            'width': e.width,
            'height': e.height,
            'data': f'data:image/png;base64,{img_b64}'
        })
    return images


def get_audio_data(tag):
    """获取音频数据"""
    events = event_acc.Audio(tag)
    audios = []
    for e in events:
        # 将音频编码为base64
        audio_b64 = base64.b64encode(e.encoded_audio_string).decode('utf-8')
        audios.append({
            'step': e.step,
            'wall_time': e.wall_time,
            'sample_rate': e.sample_rate,
            'length_frames': e.length_frames,
            'content_type': e.content_type,
            'data': f'data:{e.content_type};base64,{audio_b64}'
        })
    return audios


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
        data = get_scalar_data(tag)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/images/<path:tag>')
def api_images(tag):
    """API: 获取图像数据"""
    try:
        data = get_image_data(tag)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/audio/<path:tag>')
def api_audio(tag):
    """API: 获取音频数据"""
    try:
        data = get_audio_data(tag)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def find_event_file(directory):
    """查找事件文件"""
    if os.path.isfile(directory):
        return directory
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if 'tfevents' in file and not file.endswith('.profile-empty'):
                return os.path.join(root, file)
    return None


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python app.py <事件文件路径或目录>")
        sys.exit(1)
    
    path = sys.argv[1]
    event_file = find_event_file(path)
    
    if not event_file:
        print(f"错误: 在 {path} 中未找到事件文件")
        sys.exit(1)
    
    print(f"加载事件文件: {event_file}")
    init_event_accumulator(event_file)
    print("✅ 事件文件加载完成")
    
    
    app.run(debug=True, host='127.0.0.1', port=24433)

