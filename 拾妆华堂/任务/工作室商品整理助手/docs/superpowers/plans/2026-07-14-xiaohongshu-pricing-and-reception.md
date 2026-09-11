# 拾妆华堂小红书价目表与客户接待体系 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 交付排序后的商品数据库、小红书公开价目表图片和完整客户接待话术。

**Architecture:** 以现有工作簿生成文件作为商品价格唯一数据源，通过固定商品编号顺序生成 V1.2 工作簿。运营与接待规则单独写成 Markdown，价目表使用内置图片生成工具制作，并以设计规格中的固定文字进行视觉核验。

**Tech Stack:** JavaScript、Node.js、`@oai/artifact-tool`、Markdown、内置 `image_gen`

## Global Constraints

- 商品编号保持不变，只调整显示顺序。
- 公开价格采用固定价；人物企划与新中式婚礼标注“定制咨询”。
- 成都主城区上门在到店价基础上加 100 元服务费，往返交通实报实销。
- 图片采用 3:4 竖版、新中式留白加现代网格，不使用人物照片。
- Kevin 负责首次接待与运营，妆容专业问题转萱萱。
- 工作簿继续保持 5 张工作表并兼容飞书导入。

---

### Task 1: 调整商品排序并导出 V1.2

**Files:**
- Modify: `/Users/kevin/.codex/visualizations/2026/07/13/019f5c60-9e35-76e2-9c02-86f9044bfb36/build_workbook.mjs`
- Create: `/Users/kevin/Documents/CATmaker/01-拾妆华堂/拾妆华堂经营数据库_V1.2.xlsx`

**Interfaces:**
- Consumes: `productRows` 中 SZ001-SZ017 商品记录。
- Produces: 按固定编号顺序排列的“商品库”。

- [ ] **Step 1: 加入固定商品显示顺序**

```js
const productOrder = [
  "SZ014", "SZ015", "SZ016", "SZ017",
  "SZ002", "SZ001", "SZ003",
  "SZ005", "SZ004", "SZ006",
  "SZ011", "SZ007", "SZ008", "SZ009",
  "SZ012", "SZ010", "SZ013",
];
const rank = new Map(productOrder.map((id, index) => [id, index]));
productRows.sort((a, b) => rank.get(a[0]) - rank.get(b[0]));
```

- [ ] **Step 2: 将输出文件名改为 V1.2**

```js
const outputPath = `${outputDir}/拾妆华堂经营数据库_V1.2.xlsx`;
```

- [ ] **Step 3: 运行生成程序并复制成品到项目目录**

Run:

```bash
/Users/kevin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node build_workbook.mjs
cp /Users/kevin/.codex/visualizations/2026/07/13/019f5c60-9e35-76e2-9c02-86f9044bfb36/outputs/019f5c60-9e35-76e2-9c02-86f9044bfb36/拾妆华堂经营数据库_V1.2.xlsx /Users/kevin/Documents/CATmaker/01-拾妆华堂/
```

Expected: 程序退出码 0，项目目录出现非空 V1.2 文件。

- [ ] **Step 4: 检查商品顺序与公式错误**

Expected: 首四项为 SZ014-SZ017；公式错误扫描匹配 0 项。

### Task 2: 创建小红书运营与接待话术文档

**Files:**
- Create: `/Users/kevin/Documents/CATmaker/01-拾妆华堂/拾妆华堂_小红书运营与客户接待话术_V1.md`

**Interfaces:**
- Consumes: 设计规格中的商品名称、固定价格、角色分工和上门规则。
- Produces: 可直接复制使用的运营与接待文字模板。

- [ ] **Step 1: 写入主页和笔记编辑规则**

必须包含昵称、简介、置顶三篇、标题公式、首图要求、正文结构和行动引导。

- [ ] **Step 2: 写入前 12 篇发布顺序**

内容覆盖品牌故事、空间、客户案例、专业知识、情侣创业、新中式和服务价目。

- [ ] **Step 3: 写入完整客户接待流程**

必须包含首次回复、需求收集、商品推荐、报价、上门确认、收定金、改期、未成交跟进、服务前提醒、交付和回访。

- [ ] **Step 4: 扫描价格和占位符**

Run:

```bash
rg -n 'TBD|TODO|待补充|¥249|¥399|¥699|¥1599|上门' 拾妆华堂_小红书运营与客户接待话术_V1.md
```

Expected: 没有占位符；关键价格与上门规则出现。

### Task 3: 生成公开价目表图片

**Files:**
- Create: `/Users/kevin/Documents/CATmaker/01-拾妆华堂/拾妆华堂_公开价目表_V1.png`

**Interfaces:**
- Consumes: 设计规格中的价目表文字与视觉规则。
- Produces: 可用于小红书的 3:4 竖版 PNG。

- [ ] **Step 1: 使用内置 image_gen 生成价目表**

Prompt 内容必须要求逐字呈现：

```text
拾妆华堂
妆造与影像价目
初见·单妆 到店¥249 / 上门¥349+交通
初见·日常妆发 到店¥399 / 上门¥499+交通
臻选·东方主题妆造 到店¥699 / 上门¥799+交通
婚礼亲友妆造 到店¥399/人 / 上门¥499/人+交通
初见·肖像体验 ¥699
臻选·私人肖像 ¥1599
华堂·人物企划 定制咨询
初见·新娘试妆 ¥399
新娘私人造型 ¥1599
华堂·新中式婚礼造型 定制咨询
三环外、早班、多人、复杂发型、特殊场地及指定服饰提前确认
成都一环私人预约制妆造空间
```

- [ ] **Step 2: 检查视觉与文字**

检查品牌名、10 个商品、所有价格、上门差价和页脚说明。发现单个问题时只针对该问题迭代一次。

- [ ] **Step 3: 将最终图片复制到项目目录**

Expected: PNG 文件非空，可正常打开，手机竖屏文字清晰。

### Task 4: 最终一致性检查

**Files:**
- Verify: `拾妆华堂经营数据库_V1.2.xlsx`
- Verify: `拾妆华堂_小红书运营与客户接待话术_V1.md`
- Verify: `拾妆华堂_公开价目表_V1.png`

- [ ] **Step 1: 比较三份成品中的价格和名称**

Expected: 固定价格与设计规格一致；定制项目不出现错误固定价。

- [ ] **Step 2: 验证文件完整性**

Run:

```bash
unzip -t 拾妆华堂经营数据库_V1.2.xlsx
file 拾妆华堂_公开价目表_V1.png
test -s 拾妆华堂_小红书运营与客户接待话术_V1.md
```

Expected: Excel 压缩数据无错误；图片识别为 PNG；Markdown 非空。
