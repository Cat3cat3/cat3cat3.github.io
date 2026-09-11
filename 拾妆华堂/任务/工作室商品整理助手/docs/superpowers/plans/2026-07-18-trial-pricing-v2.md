# 拾妆华堂引流定价与运营物料 V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将已确认的引流固定价同步到商品数据库、公开价目表图片和小红书客户接待话术，并完成一致性与视觉验收。

**Architecture:** 以已确认的书面设计稿作为唯一价格源；工作簿由现有 `@oai/artifact-tool` 构建脚本生成新版本，话术以独立 V2 文档保存，价目表在现有 V1 视觉基础上生成 V2。三个交付物均保留旧版本，避免覆盖历史资产。

**Tech Stack:** JavaScript、`@oai/artifact-tool`、Markdown、OpenAI ImageGen、Excel/XLSX、PNG

## Global Constraints

- 所有交付文件位于 `/Users/kevin/Desktop/cat3cat3.github.io/拾妆华堂`。
- 固定价：轻妆自拍 99、单妆到店 199/上门 299、日常妆发到店 299/上门 399、东方主题到店 499/上门 599、婚礼亲友到店 299/人/上门 399/人、肖像体验 699、私人肖像 1599、新娘试妆 299、新娘私人造型 1599。
- 所有上门价另加交通费；特殊场景、早班、多人和复杂发型预约前确认。
- 新娘试妆确认正式预约后，299 元转为预约定金并抵扣订单；未预约则为试妆服务费。
- 轻妆自拍仅到店、单人、基础轻妆、简单发型整理、30 分钟专业相机自拍，不含摄影师跟拍和人工精修。
- 不覆盖 V1 文件；输出数据库 V1.3、价目表 V2、话术 V2。

---

### Task 1: 更新商品数据库生成脚本并导出 V1.3

**Files:**
- Modify: `/Users/kevin/.codex/visualizations/2026/07/13/019f5c60-9e35-76e2-9c02-86f9044bfb36/build_workbook.mjs`
- Create: `/Users/kevin/Desktop/cat3cat3.github.io/拾妆华堂/拾妆华堂经营数据库_V1.3.xlsx`

**Interfaces:**
- Consumes: `2026-07-18-trial-pricing-v2-design.md` 中的价格与商品排序。
- Produces: 五张工作表组成的 V1.3 工作簿，供飞书或 Excel 导入。

- [ ] **Step 1: 检查现有商品编号、排序、价格和输出路径**

Run:

```bash
rg -n "SZ0|productOrder|V1.2|output" /Users/kevin/.codex/visualizations/2026/07/13/019f5c60-9e35-76e2-9c02-86f9044bfb36/build_workbook.mjs
```

Expected: 显示现有商品数组、排序数组和 V1.2 输出文件名。

- [ ] **Step 2: 修改脚本数据**

使用 `apply_patch` 完成以下精确变更：

```text
新增 SZ018｜初见·轻妆自拍体验｜当前价 99元｜参考价 99｜测试阶段｜引流尝鲜
商品顺序将 SZ018 放在首位
SZ014 当前价 199元、参考价 199
SZ015 当前价 299元、参考价 299
SZ016 当前价 499元、参考价 499
SZ017 当前价 299元/人、参考价 299
SZ002 当前价 699元、参考价 699
SZ001 当前价 1599元、参考价 1599
SZ005 当前价 299元、参考价 299，并加入试妆抵扣规则
SZ004 当前价 1599元、参考价 1599
新增内容选题：99元轻妆自拍体验招募
输出文件名改为 拾妆华堂经营数据库_V1.3.xlsx
```

- [ ] **Step 3: 运行构建脚本**

Run:

```bash
node /Users/kevin/.codex/visualizations/2026/07/13/019f5c60-9e35-76e2-9c02-86f9044bfb36/build_workbook.mjs
```

Expected: 生成 V1.3 工作簿，无 JavaScript 或导出错误。

- [ ] **Step 4: 验证工作簿结构、公式和视觉**

使用脚本内的 `workbook.inspect` 验证五张工作表和零公式错误，并 `workbook.render` 渲染全部工作表；随后运行：

```bash
unzip -t /Users/kevin/Desktop/cat3cat3.github.io/拾妆华堂/拾妆华堂经营数据库_V1.3.xlsx
```

Expected: `No errors detected in compressed data`，渲染图无裁切、乱码或异常空白。

---

### Task 2: 生成小红书运营与客户接待话术 V2

**Files:**
- Read: `/Users/kevin/Desktop/cat3cat3.github.io/拾妆华堂/拾妆华堂_小红书运营与客户接待话术_V1.md`
- Create: `/Users/kevin/Desktop/cat3cat3.github.io/拾妆华堂/拾妆华堂_小红书运营与客户接待话术_V2.md`

**Interfaces:**
- Consumes: 最终公开价格、轻妆自拍边界、新娘试妆抵扣规则。
- Produces: 可直接复制到微信、小红书和闲鱼的运营及接待文本。

- [ ] **Step 1: 检查 V1 中所有价格与话术入口**

Run:

```bash
rg -n "价格|到店|上门|试妆|肖像|自拍|客户" /Users/kevin/Desktop/cat3cat3.github.io/拾妆华堂/拾妆华堂_小红书运营与客户接待话术_V1.md
```

Expected: 定位所有需要同步的公开报价和咨询场景。

- [ ] **Step 2: 创建 V2 文档**

使用 `apply_patch` 创建完整 V2，必须包含：

```text
完整固定价表
99元轻妆自拍的适合人群、服务边界和升级路径
单妆/妆发首次咨询话术
到店与上门费用确认话术
肖像三档推荐话术
新娘试妆299元转定金抵扣规则
未成交跟进与老客户唤醒话术
小红书首批内容结构与价格发布注意事项
```

- [ ] **Step 3: 校验价格一致性和占位符**

Run:

```bash
rg -n "99|199|299|399|499|599|699|1599|定制咨询|转为预约定金|TODO|TBD|待补充" /Users/kevin/Desktop/cat3cat3.github.io/拾妆华堂/拾妆华堂_小红书运营与客户接待话术_V2.md
```

Expected: 所有已确认价格和抵扣规则存在，不出现 TODO、TBD 或待补充。

---

### Task 3: 生成公开价目表图片 V2

**Files:**
- Read: `/Users/kevin/Desktop/cat3cat3.github.io/拾妆华堂/拾妆华堂_公开价目表_V1.png`
- Create: `/Users/kevin/Desktop/cat3cat3.github.io/拾妆华堂/拾妆华堂_公开价目表_V2.png`

**Interfaces:**
- Consumes: 最终公开价格和 V1 的新中式视觉语言。
- Produces: 竖版、可发布到小红书/朋友圈/闲鱼的 PNG 价目表。

- [ ] **Step 1: 查看 V1 图片并记录版式问题**

使用 `view_image` 查看 V1，确认标题、栏目、留白和底部说明可作为 V2 的视觉参考。

- [ ] **Step 2: 使用 ImageGen 生成 V2**

以 V1 作为参考图，生成包含以下精确文案的竖版图片：

```text
初见·轻妆自拍体验 ¥99（仅到店，不含摄影师跟拍与人工精修）
初见·单妆 到店¥199｜上门¥299＋交通费
初见·日常妆发 到店¥299｜上门¥399＋交通费
臻选·东方主题妆造 到店¥499｜上门¥599＋交通费
婚礼亲友妆造 到店¥299/人｜上门¥399/人＋交通费
初见·肖像体验 ¥699
臻选·私人肖像 ¥1599
华堂·人物企划 定制咨询
初见·新娘试妆 ¥299
新娘私人造型 ¥1599
华堂·新中式婚礼造型 定制咨询
试妆确认预约后，¥299转为预约定金并抵扣订单
三环外、早班、多人、复杂发型、特殊场地提前确认
```

Expected: 米白、墨色、朱红、少量金色，新中式但现代；文字完整清楚。

- [ ] **Step 3: 保存并视觉验收**

将生成图复制到目标 V2 文件，使用 `view_image` 以原始分辨率检查：

```text
无错别字
无乱码
无文字裁切
所有固定价格与设计稿一致
上门交通费和试妆抵扣说明可读
```

---

### Task 4: 跨文件一致性验收

**Files:**
- Verify: `/Users/kevin/Desktop/cat3cat3.github.io/拾妆华堂/拾妆华堂经营数据库_V1.3.xlsx`
- Verify: `/Users/kevin/Desktop/cat3cat3.github.io/拾妆华堂/拾妆华堂_公开价目表_V2.png`
- Verify: `/Users/kevin/Desktop/cat3cat3.github.io/拾妆华堂/拾妆华堂_小红书运营与客户接待话术_V2.md`

**Interfaces:**
- Consumes: Tasks 1–3 的三个成品。
- Produces: 可交付的统一价格与运营资产包。

- [ ] **Step 1: 核对文件存在与版本号**

Run:

```bash
ls -lh /Users/kevin/Desktop/cat3cat3.github.io/拾妆华堂/拾妆华堂经营数据库_V1.3.xlsx /Users/kevin/Desktop/cat3cat3.github.io/拾妆华堂/拾妆华堂_公开价目表_V2.png /Users/kevin/Desktop/cat3cat3.github.io/拾妆华堂/拾妆华堂_小红书运营与客户接待话术_V2.md
```

Expected: 三个文件存在且大小大于 0。

- [ ] **Step 2: 对照设计稿逐项核验**

逐项检查 9 个固定价格、4 个上门差价、2 个定制咨询、轻妆自拍边界和新娘试妆抵扣规则；任何不一致都返回对应任务修正。

- [ ] **Step 3: 最终交付**

向用户提供三个绝对路径的可点击链接，并在回复中直接展示 V2 价目表图片。
