---
name: doc-maintenance
description: 项目文档维护规范。当用户要求更新文档、讨论文档规则、同步 README 版本、发布新版本、创建 changelog、或询问"文档怎么更新"时使用。本技能强制要求：所有代码变更必须同步更新文档，文档与代码必须保持同步，双语项目所有对外文档必须中英双语。
---

# Project Documentation Maintenance / 项目文档维护规范

## Overview / 概述

This skill defines mandatory rules for keeping project documentation synchronized with code changes. **Documentation updates are a required part of code changes — they must be committed together in the same PR.**

本文档定义了项目文档与代码变更保持同步的强制规则。**文档更新是代码变更的必要组成部分——必须在同一 PR 中一起提交。**

---

## Rule 1: Language Strategy / 语言策略

### 判断标准

| 项目自身定位 | 文档语言要求 |
|-------------|-------------|
| **双语项目** — `README.md` 本身采用中英双语格式 | 全部对外文档必须中英双语，不能出现纯单语文档 |
| **单语项目** — 项目自身为纯英文或纯中文 | 各文档按项目自身语言走，不强制翻译 |

### 双语项目必须包含的文档

- `README.md` — 中英双语主入口
- `README_en.md` — 纯英文完整版（按需，见规则 2）
- `README_zh.md` — 纯中文完整版（按需，见规则 2）
- `CHANGELOG.md` — 中英双语变更日志
- `SECURITY.md` — 中英双语安全政策

**如果项目 `README.md` 本身是双语的，则 `SECURITY.md` 等所有对外文档也必须是双语的。**

---

## Rule 2: Documentation Layers / 文档分层

### 分层结构

```
README.md (中英双语)
├─ 定位：项目对外主入口，中英双语表格对照
├─ 内容：核心功能 + changelog 摘要 + 核心使用说明
└─ 原则：保持精简（建议不超过 500 行），不过度膨胀
         ↓ 当超过 500 行时，按需拆分为独立语言版本

README_en.md (纯英文) ← 按需拆分
README_zh.md (纯中文) ← 按需拆分
├─ 定位：完整信息的独立语言版本
└─ 内容：与 README.md 同步的所有详细信息
         └─ 触发条件：README.md 超过 500 行时考虑拆分

CHANGELOG.md (中英双语)
├─ 定位：变更的唯一权威记录
└─ 内容：完整变更历史，所有版本详细记录

SECURITY.md (中英双语)
├─ 定位：安全政策与已知限制
└─ 内容：漏洞报告渠道 + known limitations + wontfix 记录
```

### 同步规则

1. **`README.md` 是主入口**，其他版本必须与 `README.md` 同步
2. **`README_en.md` / `README_zh.md` 是辅助版本**，内容必须与 `README.md` 完全一致
   - 任何 `README.md` 的变更，必须同步到两个翻译版本
   - 不允许出现一方有内容另一方没有的情况
3. **`CHANGELOG.md` 是变更记录**，单独维护，不与 `README.md` 内容重叠
4. **`SECURITY.md` 独立维护**，新增安全相关修复 → 必须更新；wontfix 决策 → 必须记录

---

## Rule 3: Update Triggers / 更新触发条件（强制）

```
┌─────────────────────────────────────────────────────────┐
│            必须更新文档的情况 / Mandatory Update Triggers   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  🔴 任何代码变更后 → 必须同步更新文档，才能合并 PR          │
│                                                          │
│  具体触发项：                                             │
│  ├─ 新增 / 删除 / 重命名 文件                              │
│  ├─ API 接口变更（参数、返回值、行为）                       │
│  ├─ 配置文件结构变化                                       │
│  ├─ 依赖项变更（新增 pip / Docker image / 环境变量）        │
│  ├─ 端口号、路径变化                                       │
│  ├─ 新增功能或功能行为改变                                 │
│  ├─ Bug fix 行为说明（如果影响用户使用）                     │
│  └─ 安全相关修复（无论大小）→ 必须同步更新 SECURITY.md        │
│                                                          │
│  🟡 文档自身错误 → 随时修正，不受上述限制                   │
└─────────────────────────────────────────────────────────┘
```

**PR 合并前置条件：文档更新与代码变更同步提交，缺一不可。**

### 双语对照格式要求

所有双语文档（`README.md`、`CHANGELOG.md`、`SECURITY.md`）使用表格对照格式：

```markdown
| 中文 | English |
|------|---------|
| 变更内容描述 | Change description |
```

禁止出现纯段落式双语（中文一段、英文一段），必须表格对照。

---

## Rule 4: Version Number Convention / 版本号规范

### 格式

```
vX.Y.Z

 X (Major) — 重大架构重构，不兼容的 API 变更
 Y (Minor) — 新增功能，向后兼容的功能变更
 Z (Patch) — Bug fix，安全修复，不改变功能的改进
```

### 版本格式样例

```
## v1.2.0 (2026-04-21) ⚠️ 重大升级 / ⚠️ MAJOR UPGRADE
## v1.2.1 (2026-04-23) 🔒 安全修复 / 🔒 Security Fix
```

---

## Rule 5: Pre-release Checklist / 发布前检查清单

每次发布新版本前，依次检查：

```
发布前检查清单 / Pre-release Checklist:

 [ ] CHANGELOG.md 已记录所有变更，且格式为中英双语表格对照
 [ ] README.md changelog 摘要与 CHANGELOG.md 一致
 [ ] README_en.md / README_zh.md 与 README.md 完全同步
 [ ] SECURITY.md 如有变更已同步（含安全修复说明）
 [ ] 新增文件/接口已在项目结构章节中描述
 [ ] 项目结构章节已更新（新增文件已列入）
 [ ] 版本号已更新
 [ ] 文档无错别字、无格式错误
```

---

## Implementation Guide / 实施指南

### When Fixing Bugs / 修复 Bug 时

1. 修复代码
2. 同步更新 `CHANGELOG.md` 的 patch 版本节
3. 如 bug fix 改变用户可见行为，同步更新 `README.md` 相关章节
4. 如涉及安全修复，必须更新 `SECURITY.md`

### When Adding Features / 新增功能时

1. 实现功能代码
2. 在 `CHANGELOG.md` 的 Y 版本节记录新增功能（中英双语）
3. 更新 `README.md` 功能特性章节
4. 如 `README.md` 超过 500 行，同步更新 `README_en.md` 和 `README_zh.md`
5. 如有新文件，更新项目结构章节

### When Refactoring / 重构时

1. 完成代码重构
2. 在 `CHANGELOG.md` 记录架构变更
3. 更新 `README.md` 系统架构章节（如架构有变化）
4. 更新项目结构章节（如文件有增减）
5. 如 API 有变更，更新 API 相关文档

---

## Common Mistakes / 常见错误

| 错误 | 正确做法 |
|------|----------|
| 只更新代码，不更新文档 | 文档更新是 PR 的一部分，缺一不可 |
| `CHANGELOG.md` 只写中文 | 双语项目必须中英双语表格对照 |
| `README_en.md` 和 `README_zh.md` 不同步 | 任何 `README.md` 变更必须同步到两个翻译版本 |
| `SECURITY.md` 遗漏安全修复 | 安全相关修复必须记录到 `SECURITY.md` |
| 项目结构章节未更新 | 新增/删除文件必须同步更新项目结构章节 |

---

## Quick Reference / 快速参考

### 文档与代码必须同步的场景

```
文件新增/删除/重命名     → README.md 项目结构 + CHANGELOG.md
API 参数/返回值变更     → README.md 相关 API 文档 + CHANGELOG.md
依赖项/环境变量新增      → README.md 部署章节 + CHANGELOG.md
端口/路径变化          → README.md 访问地址章节 + CHANGELOG.md
新功能上线             → README.md 功能特性 + CHANGELOG.md
Bug fix（影响用户）    → CHANGELOG.md + 必要时更新相关章节
安全修复（任何大小）    → SECURITY.md + CHANGELOG.md
```

### 版本号自增规则

```
Breaking change (不兼容变更)     → X + 1, Y = 0, Z = 0   (例: v1.2.0 → v2.0.0)
New feature (新功能)             → Y + 1, Z = 0           (例: v1.2.0 → v1.3.0)
Bug fix / Security patch        → Z + 1                  (例: v1.2.0 → v1.2.1)
```
