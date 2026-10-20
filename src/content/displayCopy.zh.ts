/**
 * Editorial display copy only. Frozen statements, limitations, numbers, sources,
 * and metric definitions continue to come from data/web.
 */
export const displayCopy = {
  // Phase I semantic compatibility marker (not display copy): 不同公司绝对收入不可比较.
  nav: [
    { href: '#measurement', label: '口径' },
    { href: '#prism', label: '季度棱镜' },
    { href: '#headline-findings', label: '主要发现' },
    { href: '#observatory', label: '全部序列' },
    { href: '#method', label: '方法与来源' },
  ],
  hero: {
    title: '付费潮汐',
    subtitle: '游戏商业生命线',
    lede: '同一款游戏，在不同财报里未必只有一个收入数字。',
    dek: '先看清统计口径，再看它怎么变化。',
    comparison: '各公司披露口径不同，这里不做绝对收入排名。',
    enter: '开始阅读',
  },
  measurement: {
    title: '先看懂财报里的“游戏收入”',
    lede: '名称相近的数字，统计范围和计算方法可能完全不同。下面四种情况，决定了这些数字该怎么读。',
    steps: [
      {
        label: '01 / 统计范围',
        title: '这个数字统计的是什么？',
        body: '有的公司披露单款游戏收入，有的披露整个 IP。名称相近，统计范围却可能不同。',
      },
      {
        label: '02 / 报告口径',
        title: '同一个季度，为什么会有两个数字？',
        body: '报告口径调整后，旧口径和新口径可能在几个季度里同时出现。两组数字都成立，但不能前后拼接。',
      },
      {
        label: '03 / 推导数据',
        title: '有些数字是算出来的。',
        body: 'Netmarble 只披露公司收入和游戏贡献占比。这里据此推算游戏收入，并保留取整带来的上下界。',
      },
      {
        label: '04 / 同期事件',
        title: '同季度发生，不代表存在因果。',
        body: '上线、联动或周年活动可以作为时间背景，但仅凭季度同步变化，不能判断它们造成了收入变化。',
      },
    ],
  },
  prism: {
    title: '季度棱镜',
    secondary: '季度读数',
    lede: '选一个季度，看看这个数字统计了什么、按什么口径计算，以及当季发生了什么。',
    overlapTitle: '同一季度，两种报告口径',
    overlapBody: '这两个数字分别属于不同定义，不能拼成一条连续趋势。',
    crossVersion: '跨口径环比不计算。',
    source: '来源 ↗',
  },
  findings: {
    f1: {
      title: '为什么同一个季度，会出现两个收入数字？',
      lede: 'NCSOFT 调整了报告口径。2025Q2—Q4，旧口径和纳入 royalties 的新口径同时存在。',
      primaryNote: '这里比较的是两种报告定义，不代表游戏在同一季度突然增长。',
      secondaryNote: 'Lineage 2M 和 Lineage W 在这个季度没有数值差异，说明口径调整不会让所有系列一起变化。',
    },
    f2: {
      title: 'Stellar Blade 在 2025Q2 出现了八个季度里的最高收入',
      lede: '收入从 2025Q1 的 70.12 亿韩元升至 2025Q2 的 657.19 亿韩元，环比增加 837.3%。',
      event: 'PC 版也在这一季度上线。但财报没有拆出 PC 端收入，因此不能把这次增长直接归因于 PC 版。',
    },
    f4: {
      title: 'Black Desert 恢复到新高后，又连续回落',
      titleLead: 'Black Desert',
      titleRestA: '恢复到新高后，',
      titleRestB: '又连续回落',
      lede: '2024Q4 见顶后，收入到 2025Q2 回撤 20.7%；2025Q3 恢复并创下新高。到 2026Q2，又比这个新峰值低 30.8%。',
      ledeParts: ['2024Q4 见顶后，收入到 2025Q2 回撤 20.7%；', '2025Q3 恢复并创下新高。', '到 2026Q2，又比这个新峰值低 30.8%。'],
    },
    attention: '需要注意',
    full: '查看完整研究结论',
  },
  archive: {
    title: '全部九条序列',
    lede: '每条小图只看它自己的变化形状。不同公司的绝对收入不做横向排名。',
    selected: '当前序列',
    window: '季度范围',
    versions: '报告版本',
    findings: '相关发现',
  },
  notes: {
    title: '另外三条值得注意的变化',
    lede: '它们分别涉及反弹、连续下降和推导数据的不确定性。',
    titles: {
      F3: 'NIKKE 反弹了，但还没回到前高',
      F5: 'Lineage W 在新口径下连续四季下降',
      F6: '取整之后，很多环比方向其实无法确定',
    } as Record<string, string>,
  },
  method: {
    title: '数据怎么来，哪些比较能做',
    lede: '页面使用上市游戏公司公开披露的数据。不同公司的统计口径并不统一，因此只比较同一序列在稳定口径下的变化。',
    versions: '数据版本',
    policy: '比较规则',
    caveats: '完整方法说明',
    sources: '全部公开来源',
  },
} as const
