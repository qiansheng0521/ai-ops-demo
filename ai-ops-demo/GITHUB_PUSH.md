# 上传到 GitHub

本地已初始化 Git 并完成首次提交。只需补上你的 GitHub 仓库地址，执行下面命令即可推送。

## 方式一：已有远程仓库
```powershell
cd D:\Documents\ChatGPT\产品运营
git remote add origin https://github.com/<你的用户名>/ai-ops-demo.git
git branch -M main
git push -u origin main
```

## 方式二：用 GitHub CLI 创建并推送（若已安装 gh）
```powershell
gh repo create ai-ops-demo --public --source=. --remote=origin --push
```

## 首次推送前建议
- 修改提交者信息（可选）：
```powershell
git config user.name "你的名字"
git config user.email "你的邮箱"
git commit --amend --reset-author --no-edit
```
- 如果希望私有仓库，把 `--public` 改为 `--private`。

## 推送后检查
1. README 中的架构图、RFM 图、Dify 图是否正常显示。
2. `outputs/` 下的日报、文案、评论报告是否能打开。
3. 在简历里附上仓库链接，建议写：`github.com/<你的用户名>/ai-ops-demo`
