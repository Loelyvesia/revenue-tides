<script setup lang="ts">
const rows = [
  { index: '01', title: '实体', mark: 'GAME_TITLE ≠ IP', note: '先确认被报告的是单一游戏，还是发行商定义的 IP 范围。' },
  { index: '02', title: '证据', mark: '● Official / ◇ Derived', note: '派生值不是次等证据，但必须与兼容区间一起阅读。' },
  { index: '03', title: '口径版本', mark: 'legacy ║ royalty-integrated', note: '同季度可以有两个定义；口径变化不是商业增长。' },
  { index: '04', title: '范围', mark: '平台 · 地区 · 会计口径', note: '每个数值都保留发行商定义的报告范围。' },
  { index: '05', title: '语境', mark: '事件轨道 ≠ 因果箭头', note: '同期事件与发行方解释分别呈现，不升级为项目因果结论。' },
]
</script>

<template>
  <section id="primer" class="section">
    <div class="shell">
      <p class="eyebrow">S1 / MEASUREMENT PRIMER</p>
      <h2>一个收入数字由什么构成？</h2>
      <p class="lede">先拆开实体、证据、口径、范围与语境，再谈变化。</p>
      <div class="primer-ledger">
        <article v-for="row in rows" :key="row.index">
          <span class="row-index numeric">{{ row.index }}</span>
          <h3>{{ row.title }}</h3>
          <strong class="numeric">{{ row.mark }}</strong>
          <p>{{ row.note }}</p>
        </article>
      </div>
      <div class="evidence-legend" aria-label="证据图例">
        <span><i class="direct"></i>Official reported</span>
        <span><i class="derived"></i>Derived from official + interval</span>
        <span><i class="event"></i>Event context</span>
        <span><i class="claim"></i>Issuer explanation</span>
        <span><i class="seam"></i>Metric version change</span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.primer-ledger { margin-top: 2.5rem; border-top: 2px solid var(--text-primary); }.primer-ledger article { display: grid; grid-template-columns: 3rem 7rem minmax(12rem, .9fr) 1.4fr; gap: 1rem; align-items: baseline; padding-block: 1rem; border-bottom: 1px solid var(--rule-border); }.primer-ledger h3 { font-size: 1rem; }.primer-ledger p { margin: 0; }.row-index { color: var(--text-secondary); }
.evidence-legend { display: flex; flex-wrap: wrap; gap: 1rem 1.5rem; margin-top: 1.5rem; padding: 1rem; border: 1px solid var(--rule-border); background: var(--surface-primary); }.evidence-legend span { display: inline-flex; align-items: center; gap: .5rem; font-size: .8rem; }.evidence-legend i { display: inline-block; width: .8rem; height: .8rem; }.direct { border-radius: 50%; background: var(--evidence-direct); }.derived { border: 2px solid var(--evidence-derived); transform: rotate(45deg); }.event { border-left: 3px solid var(--event); border-bottom: 1px solid var(--event); }.claim { border: 2px solid var(--event); }.seam { border-inline: 2px solid var(--text-primary); }
@media (max-width: 767px) { .primer-ledger article { grid-template-columns: 2rem 1fr; }.primer-ledger article strong, .primer-ledger article p { grid-column: 2; } }
</style>
