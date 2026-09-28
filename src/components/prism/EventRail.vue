<script setup lang="ts">
import type { AttributedClaim, EventRecord } from '../../types/webData'

defineProps<{
  events: EventRecord[]
  claims: AttributedClaim[]
  quarter: string
}>()
</script>

<template>
  <section class="event-rail" aria-label="事件语境轨道">
    <div class="rail-heading">
      <span class="eyebrow">EVENT CONTEXT · CURATED / NON-CAUSAL</span>
      <span class="annotation">事件覆盖经策展且非穷尽；同季度不等于因果。</span>
    </div>
    <div v-if="events.length" class="event-items">
      <article v-for="event in events" :key="event.event_id" class="event-item">
        <span class="event-tick" aria-hidden="true"></span>
        <div>
          <strong>{{ event.name }}</strong>
          <p class="annotation numeric">{{ event.start_date }} · {{ event.platform_scope }} · 与 {{ quarter }} 同期</p>
        </div>
      </article>
    </div>
    <p v-else class="empty-context">本季度没有收录的官方事件。No curated event in this quarter.</p>
    <div v-if="claims.length" class="issuer-claims">
      <h4>发行方说明 · Issuer explanation</h4>
      <article v-for="claim in claims" :key="claim.claim_id">
        <strong>{{ claim.issuer }}</strong>
        <p>{{ claim.summary }}</p>
        <span class="annotation">发行方归因，不是本项目的因果结论。</span>
      </article>
    </div>
  </section>
</template>

<style scoped>
.event-rail { margin-top: 1.25rem; padding-top: 1rem; border-top: 2px solid var(--event); }
.rail-heading { display: flex; justify-content: space-between; gap: 1rem; align-items: baseline; }
.event-items { display: grid; gap: 0.75rem; margin-top: 0.75rem; }
.event-item { display: grid; grid-template-columns: 1rem 1fr; gap: 0.6rem; }
.event-tick { width: 0.75rem; height: 1.25rem; border-left: 3px solid var(--event); border-bottom: 1px solid var(--event); }
.event-item p { margin: 0.15rem 0 0; }
.empty-context { margin: 0.75rem 0 0; color: var(--text-secondary); }
.issuer-claims { margin-top: 1rem; padding: 1rem; border: 1px solid var(--event); background: var(--surface-primary); }
.issuer-claims h4 { margin: 0 0 0.5rem; }
.issuer-claims p { margin: 0.25rem 0; }
@media (max-width: 767px) { .rail-heading { display: block; } }
</style>
