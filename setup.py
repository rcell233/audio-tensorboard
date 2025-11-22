#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# 读取README
def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

# 读取requirements
def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='audiotensorboard',
    version='0.1.0',
    author='AudioTensorBoard Contributors',
    author_email='',
    description='现代化的TensorBoard日志可视化工具，支持音频、图像和标量数据',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/rcell233/audio-tensorboard',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'atb': ['templates/*.html'],
    },
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'atb=atb.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.7',
    keywords='tensorboard visualization machine-learning deep-learning audio',
    project_urls={
        'Bug Reports': 'https://github.com/rcell233/audio-tensorboard/issues',
        'Source': 'https://github.com/rcell233/audio-tensorboard',
    },
)

