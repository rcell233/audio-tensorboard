# AudioTensorBoard

现代化的 TensorBoard 日志可视化工具，优化音频相关的显示。由cursor自动化生成，优化中。。。

## 安装

```bash
pip install git+https://github.com/rcell233/audio-tensorboard.git
```

## 使用

```bash
# 启动（默认每10秒自动增量刷新）
atb 日志目录/

# 指定端口和刷新间隔
atb 日志目录/ --port 8080 --reload-interval 30

# 外网访问
atb 日志目录/ --host 0.0.0.0
```

