# BuildBuddy 🚀

原名 **Big Jump**，现在统一更名为 **BuildBuddy**。调用名改为 `$buildbuddy`，新安装目录为 `buildbuddy`；已有安装不会自动改名。

> **从“不知道做什么”，到第一个验证过的软件产品。**

[![check-skill](https://github.com/LysanderPhong/buildbuddy/actions/workflows/check-skill.yml/badge.svg)](https://github.com/LysanderPhong/buildbuddy/actions/workflows/check-skill.yml) · 🌐 [网站](https://lysanderphong.github.io/buildbuddy/index.zh.html) · [English README](README.md)

BuildBuddy 把编程 Agent 变成一个自主执行的“建设者 + 教练”。你可以给它一个模糊想法，也可以只说自己会什么、身边有什么麻烦，以及想做作品集还是尝试第一笔软件收入。它会先帮你选方向，再收缩出最小可用版本、选择实际路线、按可测试的切片实现，并通过真实入口验证。

## 写给学过编程、却还没做出真实项目的学生

你可能会一点 Python、Java、前端或数据分析，也完成过不少课程作业；但你还没有一个能交给真人使用、能验证、也能由自己讲清楚的作品。这个项目最初关注的，正是许多 985/211 学生也会遇到的落差：学过不少，却不知道怎样从知识走到一个真实用户。学校标签不是门槛，处在同一阶段的人都适用。

有人想做一份可信的作品集，也有人看到别人接网页单、卖小工具或做独立产品后，想试着获得第一笔软件收入。无论动机是什么，真正缺的通常不是更多教程，而是选出一个接触得到的问题、找到首位用户，并把第一版做小。

BuildBuddy 就是为这种“学过不少，却缺第一条落地路径”的时刻准备的。它不会给你一串所谓“暴利项目”，也不承诺写完网页就能赚钱。网站只是交付形式；真正需要依次验证的是：谁有一个具体问题、最小版本能不能解决、对方会不会继续使用，以及是否真的愿意付费。

它会把第一步缩成：

1. 从同学、社团、实验室、家人或熟悉的小组织里，找一个你本周就能接触到的真实问题；
2. 只给不超过三个方向，并推荐一个零或低成本、几次专注投入就能验证的默认选择；
3. 先做一个能让首位真实用户完成核心任务的版本，而不是把功能堆满；
4. 分开记录“技术可用”“有人使用”“重复使用”和“愿意付费”的证据，再决定扩展、换方向或停止。

可以直接这样开始：

> 我是大二学生，会一点 Python 和前端，但只做过课程作业。看到别人做网页赚钱，我也想试试，却不知道从哪开始。请先从我能接触到的同学、社团和实验室问题里给出不超过三个方向，推荐一个零预算选择，再带我做出首位真实用户能试的最小版本。不要承诺收入，也不要未经允许部署。

它不再是一套“做静态小网页”的固定配方，而是可以选择并组合：

- 浏览器应用和全栈产品；
- API、任务队列、数据库和后端服务；
- CLI、批处理任务和安全自动化；
- 数据管道、模型、RAG 和 LLM 系统；
- 可复用的库与 SDK；
- 移动端和桌面端应用；
- 在已有代码仓库中完成较大的功能改造。

最终交付可以是公网网站、经过测试的 API、可安装 CLI、可复现实验或模型、打包好的库，也可以是 App 构建产物。BuildBuddy 不会强迫所有项目最后都变成一个网址。

## 三步上手

1. **安装** —— 克隆仓库后运行 `bash install.sh`。
2. **说出结果或处境** —— 有方向可以说：“做一个根据 EXIF 日期安全重命名照片的 CLI”；没方向可以说：“我会一点 Python，想做第一个真实项目，先帮我从身边问题里选一个。”
3. **检查证据** —— BuildBuddy 在本地实现、运行符合技术栈的检查、说明没验证到的部分，并在尚未授权的外部操作前停下来。

## 它和普通编程提示词的区别

| 普通编程提示词 | BuildBuddy |
|---|---|
| 立刻选择一个熟悉的框架 | 先检查仓库，再按产品的真实入口选择路线 |
| 所有项目套同一套测试 | 分别使用浏览器、API、子进程、数据、干净安装或模拟器证据 |
| 只说“测试通过” | 每项结论都对应一条新鲜命令或真实操作，并说明验证边界 |
| 默认已有文件都能重写 | 记录未提交状态，未经允许不 stash、不提交、不丢弃用户改动 |
| 有登录状态就部署 | 把“有能力操作”和“用户同意操作”分开，并验证最终交付版本 |
| 重试固定次数后就停 | 只要还有不同且安全的诊断路径，就继续推进 |

## 技能结构

核心 `SKILL.md` 刻意保持精简，只放路线选择、构建循环、安全边界、证据规则和最终验收。根据具体项目按需加载：

- `references/project-profiles.md` —— Web、后端、CLI、数据/AI、库、移动/桌面、已有仓库及风险覆盖层；
- `references/verification-playbook.md` —— 快速/完整证据集与真实边界验证；
- `references/guided-mode.md` —— 无法运行命令时如何诚实协作；
- `references/release-and-deployment.md` —— 网站、API、软件包、模型和 App 的交付；
- `references/ideation-and-coaching.md` —— 找方向、教学和复盘；
- `assets/PROJECT_NOTES.template.md` —— 可选的目标与验证记录模板；
- `evals/evals.json` —— 真实触发、反例和项目路线场景；
- `scripts/validate_skill.py` —— 不依赖第三方库的结构校验器；
- `scripts/test_validator.py` / `scripts/test_installer.py` —— 负向校验与原子更新回归测试。

这种“渐进加载”方式不会把无关技术栈的规则全部塞进 Agent 上下文，同时保留需要时可读取的细节。

## 安全与诚实边界

- 优先使用仓库现有工具，不随意增加框架、Git hook 或测试包装层。
- 不会偷偷暂存无关文件、覆盖 hook、stash 用户工作、force-push 或使用破坏性 Git 恢复。
- 测试优先使用样例、临时目录、一次性数据库、服务商测试模式和干净消费项目。
- 不把正则密钥扫描当成绝对证明，不虚构或暴露凭证；怀疑泄漏时先让账号所有者撤销或轮换。
- 结果明确标记为“已验证”“部分验证”或“未验证”。
- 当前请求若已经明确授权修改、推送或部署指定目标，就把它视为本次任务的有效授权，不重复询问。

## 安装

### Codex

```bash
bash install.sh
```

安装器会先在目标旁边搭好并校验完整技能，再替换旧版本；它会拒绝危险的软链接目录，并记录内容指纹。以后重新运行即可安全更新，不再只下载单独的 `SKILL.md`。

目标目录名必须叫 `buildbuddy`：安装器会拒绝其他名称，避免误装到错误的文件夹。如果要装到别的位置，请把 `BUILDBUDDY_SKILL_DIR` 指向一个以 `buildbuddy` 结尾的路径：

```bash
BUILDBUDDY_SKILL_DIR=/my/own/skills/buildbuddy bash install.sh
```

### skills.sh（任何兼容 Agent Skills 的工具）

```bash
npx skills add lysanderphong/buildbuddy
```

适用于 Claude Code、Cursor、Codex 以及 [skills.sh](https://skills.sh/LysanderPhong/buildbuddy) 支持的所有其他智能体。

### 其他兼容 Agent Skills 的工具

请复制完整目录，包括 `SKILL.md`、`references/`、`assets/`、`agents/`、`evals/` 和 `scripts/`。不要只复制 `SKILL.md`，因为核心文件会按需加载项目类型说明。

## 使用示例

> 做一个本地优先的 AA 分账网页，不要账号，刷新后余额还在，但暂时不要部署。

> 在这个 FastAPI 仓库里增加 Postgres 导入接口。保留我无关的未提交改动，不要碰生产数据。

> 把这些交易 CSV 做成欺诈风险基线。按时间切分，与朴素基线对比，不要夸大准确率。

> 做一个 Android 和 iOS 的 Flutter 习惯打卡器。我没有 Apple 签名凭证，请准确说明实际验证了什么。

如果没有自动触发，可以直接说：**“使用 buildbuddy 这个 skill。”**

## 设计来源

BuildBuddy 使用全新编写的指令与模板，只吸收了 [OpenAI 当前技能规范](https://learn.chatgpt.com/docs/build-skills)、[Agent Skills 标准](https://github.com/agentskills/agentskills)、[GitHub Spec Kit](https://github.com/github/spec-kit)、[Anthropic skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) 和 [Superpowers](https://github.com/obra/superpowers) 的通用流程思想，包括渐进加载、结果优先的规划、符合技术栈的验证、真实场景评测，以及“先有新鲜证据再声称完成”。

仓库没有打包或直接复制第三方技能原文与模板。

## 仓库文件

- `SKILL.md` —— Agent 实际加载的英文运行指令；
- `notes/SKILL-zh.md` —— 中文阅读版；
- `README.md` / `README.zh.md` —— 英文和中文项目主页；
- `docs/` —— 双语 GitHub Pages 展示页；
- `install.sh` —— 带回滚、路径保护、来源记录和校验的原子目录安装器；
- `.github/workflows/check-skill.yml` —— CI 校验与安装测试；
- `LICENSE` —— MIT。

## 许可

MIT
