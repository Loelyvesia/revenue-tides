<script setup lang="ts">
import type { Caveat } from '../../types/webData'

defineProps<{ caveats: Caveat[] }>()
</script>

<template>
  <details class="caveat-key">
    <summary>证据边界 · Evidence key</summary>
    <ul>
      <li v-for="caveat in caveats" :key="caveat.caveat_id">
        <strong>{{ caveat.text_zh }}</strong>
        <span lang="en">{{ caveat.text_en }}</span>
      </li>
    </ul>
  </details>
</template>

<style scoped>
.caveat-key { border-block: 1px solid var(--rule-border); padding-block: 0.5rem; }
summary { min-height: 44px; display: flex; align-items: center; cursor: pointer; font-weight: 650; }
ul { margin: 0; padding: 1rem 0 0; list-style: none; columns: 2; column-gap: 2rem; }
li { break-inside: avoid; margin-bottom: 1rem; }
strong, span { display: block; font-size: 0.875rem; }
span { margin-top: 0.2rem; color: var(--text-secondary); }
@media (max-width: 767px) { ul { columns: 1; } }
</style>
