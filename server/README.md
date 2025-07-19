# InsightX Server
> 为大数据工程而打造的便捷式工具箱

## 支持的功能
|API|功能|
|--|--|
|`/mount/`|模型挂载|
|`/view/`|检视已挂载模型|
|`/view/{}`|获取模型结构|
|`/to/dtype/{}/{}`|dtype转换|
|`/to/device/{}/{}`|设备转换|

## 部署
您需要首先安装引用包以确保您可以运行InsightX Server
`pip install -r requirements.txt`

运行服务端

```bash
python -m uvicorn main:app --reload
```

我们建议您再运行我们的检查工具以确保您的环境。

```bash
python utils/env_check.py
```

如果您需要一份检测报告，请您执行

```bash
python utils/env_check.py --save
```

## 问题反馈
我们支持您在PR中询问有关此工具的问题。
## 附言
我们的工程团队不希望您过度依赖此工具，成为一名合格的大数据工程师，是不需要使用这些工具的。
