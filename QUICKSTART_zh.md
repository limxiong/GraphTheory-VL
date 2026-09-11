# GraphTheory-VL v1.0 中文使用指南

解压核心ZIP后进入`GraphTheory-VL-v1.0`目录。准备Python 3.9或更新版本，以下操作不需要安装第三方库、配置API密钥或联网。

## 1. 先读取两道题

```sh
python3 examples/read_dataset.py --split hard --limit 2
```

命令会显示Hard20的两道题目及其本地图片路径。读取完整正式集时，将`hard`改为`challenge`。题库共62题，Hard20包含在这62题中。

也可以直接用标准库读取：

```python
import json
from pathlib import Path

root = Path(".")  # 在解压后的包根目录运行
questions = [json.loads(line) for line in
             (root / "data/questions.jsonl").read_text(encoding="utf-8").splitlines()
             if line.strip()]
question = questions[0]
print(question["problem_id"], question["question"])
image_file = root / question["image_path"]
print(image_file.resolve())
```

`answer`和`explanation`是参考答案与解析，评测时不要一起发给待测模型。

## 2. 验证数据并复算已有成绩

```sh
python3 tools/verify_package.py
python3 tools/evaluate.py summarize --output results/local_summary.json
```

验证成功会输出JSON状态。汇总读取现有984条评分记录，按题计算Acc@1、MeanAcc、Pass@4和Stable@4，并与已存论文的9组指标核对。指标JSON中的数值范围为0–1，乘100后为百分比。

这里复算的是已存标签的统计结果；既有置信区间与配对比较保存在`results/paper_metrics.json`中。

## 3. 评测自己的模型

包内附有两条既有模型回答作为格式样例，可以先直接运行：

```sh
python3 tools/evaluate.py prepare --predictions examples/predictions.sample.jsonl --output pending_judgments.jsonl
```

这两条是历史回答副本，输出评分保持Pending，便于查看待判分格式。

每次预测保存为一行JSON，包含模型标识`provider`、输入条件`condition`、题号`problem_id`、轮次`roll`和模型输出`response`或`answer`。原图条件写`original`，仅文本条件写`text_only`，轮次为1–4。完整流程及格式见[评测说明](EVALUATION.md)。

```sh
python3 tools/evaluate.py prepare --predictions my_predictions.jsonl --output pending_judgments.jsonl
```

工具补上参考答案和字符串匹配提示，评分仍为`Pending`。由人工或语义评判程序完成判分并记录依据后，再执行：

```sh
python3 tools/evaluate.py summarize --labels judged_predictions.jsonl --output my_metrics.json
```

程序会同时报告覆盖情况，仅在一题四轮标签齐全时把它纳入四项指标。`Pending`或`Missing`不会自动计为错误，重复的模型／条件／题目／轮次会报错。

## 4. 查看完整模型回答

另行解压`GraphTheory-VL-v1.0-responses.zip`，阅读其中README和题目索引。该附件包含当前984个评分位置所关联的983份完整回答、判分记录、评分参考和提示词。缺少完整正文的那1条用户裁决保留其实际状态。

核心包无需这个附件也能加载题目和汇总已有评分。两个包都使用包内相对路径，可以移动到其他目录。
