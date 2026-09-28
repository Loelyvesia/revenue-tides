<script setup lang="ts">
const rows = [
  { index: 'A', title: 'ENTITY / 实体', left: 'GAME_TITLE', right: 'IP', note: '单一游戏与发行商定义的 IP 范围保持分离。', kind: 'entity' },
  { index: 'B', title: 'EVIDENCE / 证据', left: '● DIRECT', right: '◇ DERIVED', note: '派生观察始终携带兼容区间与方向稳定性。', kind: 'evidence' },
  { index: 'C', title: 'VERSION / 口径', left: 'legacy', right: 'royalty-integrated', note: '定义缝两侧不拼接，不计算跨版本环比。', kind: 'version' },
  { index: 'D', title: 'CONTEXT / 语境', left: 'trajectory', right: 'event rail', note: '事件在独立轨道中提供同期背景，不构成因果。', kind: 'context' },
]
</script>

<template>
  <section id="primer" class="section">
    <div class="shell">
      <div class="section-heading">
        <span class="section-index">01 / MEASUREMENT</span>
        <div class="section-copy"><p class="eyebrow">MEASUREMENT GRAMMAR</p><h2>一个收入数字由什么构成？</h2><p class="lede">先拆开实体、证据、口径与语境，再谈变化。</p></div>
      </div>
      <div class="grammar" aria-label="商业观察测量语法">
        <article v-for="row in rows" :key="row.index" :class="['grammar-row', `grammar-${row.kind}`]">
          <span class="row-index numeric">{{ row.index }}</span>
          <h3>{{ row.title }}</h3>
          <div class="grammar-expression">
            <strong class="numeric">{{ row.left }}</strong>
            <span class="grammar-connector" aria-hidden="true"><i></i></span>
            <strong class="numeric">{{ row.right }}</strong>
          </div>
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
.grammar { border-block: 2px solid var(--text-primary); }.grammar-row { display: grid; grid-template-columns: 2.5rem 10rem minmax(20rem, 1.15fr) minmax(16rem, .85fr); gap: 1.5rem; align-items: center; min-height: 7rem; border-bottom: 1px solid var(--rule-border); }.grammar-row:last-child { border-bottom: 0; }.grammar-row h3 { font-size: .78rem; line-height: 1.4; letter-spacing: .08em; }.grammar-row p { margin: 0; color: var(--text-secondary); }.row-index { align-self: start; padding-top: 2.55rem; color: var(--text-tertiary); }
.grammar-expression { display: grid; grid-template-columns: 1fr minmax(3rem, .55fr) 1fr; gap: .75rem; align-items: center; }.grammar-expression strong { font-size: clamp(.9rem, 1.5vw, 1.1rem); }.grammar-expression strong:last-child { text-align: right; }.grammar-connector { position: relative; height: 1.25rem; border-inline: 1px solid var(--rule-border); }.grammar-connector::before { content: ''; position: absolute; top: 50%; inset-inline: 0; border-top: 1px solid var(--rule-border); }.grammar-connector i { position: absolute; top: calc(50% - 3px); left: calc(50% - 3px); width: 6px; height: 6px; background: var(--accent-primary); transform: rotate(45deg); }
.grammar-version .grammar-connector { border-inline: 3px double var(--text-primary); }.grammar-context .grammar-connector::before { border-color: var(--event); }.grammar-context .grammar-connector i { background: var(--event); }
.evidence-legend { display: flex; flex-wrap: wrap; gap: 1rem 1.75rem; margin-top: 1.5rem; padding-top: 1.25rem; border-top: 1px solid var(--rule-grid); }.evidence-legend span { display: inline-flex; align-items: center; gap: .5rem; color: var(--text-secondary); font: .72rem var(--font-numeric); }.evidence-legend i { display: inline-block; width: .75rem; height: .75rem; }.direct { border-radius: 50%; background: var(--evidence-direct); }.derived { border: 2px solid var(--evidence-derived); transform: rotate(45deg); }.event { border-left: 3px solid var(--event); border-bottom: 1px solid var(--event); }.claim { border: 2px solid var(--event); }.seam { border-inline: 2px solid var(--text-primary); }
@media (max-width: 900px) { .grammar-row { grid-template-columns: 2rem 8rem 1fr; padding-block: 1.25rem; }.grammar-row p { grid-column: 3; }.row-index { padding-top: .2rem; } }
@media (max-width: 767px) { .grammar-row { grid-template-columns: 1.5rem 1fr; gap: .6rem 1rem; }.grammar-row h3, .grammar-row p, .grammar-expression { grid-column: 2; }.grammar-expression { grid-template-columns: 1fr 2.5rem 1fr; min-height: 2.5rem; }.evidence-legend { display: grid; grid-template-columns: 1fr 1fr; } }
</style>
