# 付费潮汐——游戏商业生命线

**Revenue Tides — The Commercial Life of Games**

Status: `COMPLETE / FROZEN`  
Data cutoff: `2026-09-22`

## 1. 项目简介

一份财报里的“游戏收入”，可能指一款游戏，也可能指整个 IP 或多个平台的合计。《付费潮汐——游戏商业生命线》整理上市游戏公司的公开披露，先说明每个数字的统计对象、报告口径、证据和不确定性，再比较同一序列在稳定口径下的季度变化。项目不重建所谓“全球真实流水”，也不把不同公司的数字做绝对排名。

Revenue Tides examines fiscal-quarter commercial trajectories of publisher-defined games, IPs, and franchises using official public disclosures. Rather than reconstructing a universal “true revenue” metric, it preserves reporting definitions, evidence types, metric versions, uncertainty, and contemporaneous events so that every number retains its provenance and limits.

## 2. 研究问题

公开财报能否支持一套可复核的游戏商业轨迹研究？当数据来自不同发行商、不同实体范围与不同会计口径时，哪些变化可以在同一稳定序列内讨论，哪些比较必须停止？

## 3. 为什么“收入”需要定义

这里的数值是发行商定义的会计或商业披露，不是统一的全球市场指标。`GAME_TITLE` 与 `IP` 不合并；`OFFICIAL_REPORTED` 与 `DERIVED_FROM_OFFICIAL` 不等同；NCSOFT 的 legacy 与 royalty-integrated 指标不拼接。缺失值不是零，事件同期也不等于事件导致变化。

## 4. 数据范围

- 4 家上市游戏公司，9 条分析序列
- 75 个财政季度观察，窗口为 2024Q3–2026Q2
- 26 个精选官方事件，3 条发行商归因说法
- 18 个由官方披露推导、并保留上下界的观察
- 6 个正式 Findings，头条 Findings 为 F1、F2、F4

## 5. 来源类型

定量主干只使用公司投资者关系材料、业绩演示、factsheet 与官方披露。官方游戏或发行商页面提供事件日期。Sensor Tower 与 AppMagic 不构成本项目定量主干。公开站点链接可能重定向或拒绝自动请求；这类远端行为与应用内链接是否正确分开记录。

## 6. 六个 Findings

1. **F1：同一季度，报告口径也会改变数值。** Lineage M 在 2025Q2–2025Q4 的 royalty-integrated 数值比 legacy 高 67.97亿–134.55亿韩元；这是定义差异，不是增长。
2. **F2：Stellar Blade 的 PC 上线季度形成窗口峰值。** 2025Q1 的 70.12亿韩元升至 2025Q2 的 657.19亿韩元，环比 +837.3%；PC 上线发生在同一季度，但没有 PC 单独金额，也不推断因果。
3. **F3：NIKKE 反弹，但尚未回到前高。** 2026Q2 环比 +32.4%，仍低于 2025Q2 峰值 4.1%，状态为 `NOT_RECOVERED_WITHIN_OBSERVED_WINDOW`。
4. **F4：Black Desert 在一次恢复后再次进入回撤。** 先从 2024Q4 峰值回撤 20.7%，2025Q3 创新峰；至 2026Q2 又低于新峰 30.8%，观察窗口内尚未恢复。
5. **F5：Lineage W 新口径窗口连续四季下降。** 仅限 royalty-integrated v2 的 2025Q2–2026Q2，期末比窗口起点低 35.3%，不向前连接 legacy。
6. **F6：取整占比使多数派生环比方向无法确定。** 15 个可比较变化中 9 个方向敏感、6 个方向稳定，方向敏感占 60.0%。

## 7. 核心交互

**季度棱镜（Quarter Prism）**让读者选择一条序列和一个季度，同时查看数值、实体、报告版本、证据、推导区间、同期事件、发行商解释和来源。同季度存在两个报告口径时，两条观察会并列出现；事件始终留在独立时间轨上。

## 8. 视觉设计

页面以暖纸色为底，用深青、水绿和珊瑚色区分数据、推导区间与事件。季度序列采用有厚度的带状轨迹，但所有可读取节点仍只对应真实季度。大字号先讲结论，完整 Finding、限制和来源保留在可展开的证据层。

## 9. 数据方法

主要时间单位为财政季度。语料按连续性、实体范围、指标定义与证据类别筛选。允许的定量证据仅为 `OFFICIAL_REPORTED` 与 `DERIVED_FROM_OFFICIAL`。转换仅在稳定指标版本内部执行，包括 QoQ、基线指数、滚动峰值、回撤与恢复。派生值保留点估计、上下界、取整说明与方向稳定性。

## 10. 证据与可比性边界

不同公司的发行商定义指标不能进行绝对收入排名或高低比较。项目不做 USD 归一化、市场份额推断或跨版本 QoQ。事件只作为同期背景；发行商解释以 attributed claim 保存，不转写为项目事实。

## 11. 技术栈

Vue 3、TypeScript、Vite、原生 SVG 与 CSS。应用为静态站点，无后端、无分析追踪、无外部图表库。初始只读取 5 个 bootstrap JSON；来源表与九条序列详情按需加载。

## 12. 项目结构

主要目录说明见 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)。冻结研究位于 `research/` 与 `data/`；浏览器消费的公共数据来自 `data/web/`，并由确定性脚本同步到 `public/data/`。

## 13. 本地开发

要求 Node.js 24.x、npm 11.x 与 Python 3.13.x。首次安装依赖：

```bash
npm install
```

启动开发服务器：

```bash
npm run dev
```

## 14. 构建

```bash
npm run build
```

该命令先运行确定性数据同步，再做 TypeScript 检查并生成唯一的 `dist/`。

## 15. 预览

```bash
npm run preview
```

预览应通过 HTTP 访问，不使用 `file://`。

## 16. 可复现性

完整环境、离线数据阶段与验证命令见 [REPRODUCIBILITY.md](REPRODUCIBILITY.md)。已有本地 canonical/web 数据的重建不依赖网络、登录或私有 API。

## 17. 浏览器支持测试

生产构建在 Chrome 153、Edge 149 与 Firefox 156 中通过；测试视口为 1440×900、1280×800、1024×768、768×1024、390×844 与 320×700。WebKit/Safari-equivalent 未在可用环境中测试。

## 18. 无障碍状态

键盘、焦点、跳转链接、ARIA/live region、可访问 SVG、非颜色单一编码、减少动态、44 px 触控目标、200% 等效回流与 accessibility tree 已检查。没有可用的真实交互式屏幕阅读器会话，因此不声称完整屏幕阅读器认证或 WCAG 认证。

## 19. 性能

最终 Phase J 基线为 JS 107.29 kB / 40.27 kB gzip，CSS 26.78 kB / 5.71 kB gzip，HTML 0.91 kB。初始生产加载为 8 个请求，其中 5 个 bootstrap JSON 共 29,486 bytes；不会一次加载全部序列。

## 20. 局限

发行商指标异质、跨公司绝对值不可比；这些数值不是全球消费者支出。NCSOFT 版本不能拼接，Netmarble 派生序列受官方取整占比影响。事件覆盖经过筛选且非穷尽，时间接近不证明因果。观察窗口内未恢复不等于永久衰退。部分远端来源会变化或拒绝自动访问。

## 21. 版本与冻结状态

- Method: `revenue-tides-method-freeze-1.0.0`
- Findings: `revenue-tides-findings-1.0.0`
- Web Data: `revenue-tides-webdata-1.0.0`
- Release: `revenue-tides-release-1.0.0`
- Current presentation: `UI 2.4 FINAL REVIEW FIX`
- GitHub Pages: https://loelyvesia.github.io/revenue-tides/
- Source branch: `ui-signature-2.1`; Pages branch: `main` (static production output).

Project 02 的研究方法、语料与 Finding 已完成 Phase K 审计并冻结为 `COMPLETE / FROZEN`。UI 2.2 只调整展示文案和视觉层级；任何新增季度、口径、来源或 Finding 仍须建立新版本或走书面 amendment 流程。
