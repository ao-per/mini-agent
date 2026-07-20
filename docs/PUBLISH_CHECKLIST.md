# GitHub 发布检查表

## 仓库内容

- [ ] README 中的 `<你的仓库地址>` 已替换为真实地址；
- [ ] `.env` 未被 Git 跟踪，`.env.example` 中没有真实密钥；
- [ ] `notes/` 中没有个人、公司或客户信息；
- [ ] `evals/results/` 中没有敏感对话或模型响应；
- [ ] 选择并添加合适的开源许可证；
- [ ] 项目描述、Topics 和仓库可见性已经确认。

## 质量检查

```powershell
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
```

- [ ] 上述命令全部通过；
- [ ] 从一个全新目录按照 README 完成过安装；
- [ ] GitHub Actions 首次运行通过；
- [ ] 至少手动完成计算、时间和笔记搜索三个演示任务；
- [ ] 真实模型评测报告已检查，简历没有引用未经验证的通过率。

## Git 历史

- [ ] `git status` 中只有计划提交的文件；
- [ ] 没有提交 `.env`、缓存、虚拟环境或生成的评测报告；
- [ ] 提交信息描述清楚，例如 `docs: prepare project for portfolio`；
- [ ] 推送前再次检查 staged diff。

## GitHub 页面建议

仓库描述：

> A minimal, testable and evaluable tool-calling agent in Python.

建议 Topics：

```text
python  ai-agent  tool-calling  llm  pydantic  pytest  evaluation
```

建议置顶展示顺序：README 项目亮点、架构图、测试结果、评测设计、面试材料。
