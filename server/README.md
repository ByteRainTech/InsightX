# InsightX Server

> *为大数据工程而打造的便捷式工具箱*

## 支持的功能

> 若要查看 API，您可以打开[ApiFox](https://insightx.apifox.cn/)查看我们的 API。

| API-Path           | 功能           |
| ------------------ | -------------- |
| `/mount/`          | 模型挂载       |
| `/view/`           | 检视已挂载模型 |
| `/view/{}`         | 获取模型结构   |
| `/to/dtype/{}/{}`  | dtype 转换     |
| `/to/device/{}/{}` | 设备转换       |

## 部署
您可以使用下列命令进行安装部署
#### 环境安装
```bash
pip install -r requirements.txt
```
#### 运行服务端
```bash
uvicorn main:app --reload
```
## 在虚拟环境部署
您可以使用现代化的 `UV` 来进行 InsightX Server 的包管理。
使用`uv venv`创建虚拟环境
#### 运行服务端
```bash
uv run uvicorn main:app --reload
```

## 问题反馈

我们支持您在 [Issues](https://github.com/ByteRainTech/InsightX/issues) 中询问有关此工具的问题。
> 👏 欢迎PR

## 附言

我们的工程团队不希望您过度依赖此工具，成为一名合格的大数据工程师，是不需要使用这些工具的。
