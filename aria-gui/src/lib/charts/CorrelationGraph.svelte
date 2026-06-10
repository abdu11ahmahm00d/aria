<script lang="ts">
  import type { Flag } from '../types'
  import { findCorrelations } from '../utils'

  interface Props {
    flags: Flag[]
    class?: string
  }

  let { flags, class: className = '' }: Props = $props()
  let correlations = $derived(findCorrelations(flags))
</script>

<div class={className}>
  <div class="text-label text-text-muted mb-3">CORRELATIONS</div>
  {#if correlations.length > 0}
    <div class="space-y-2">
      {#each correlations as corr}
        <div class="flex items-center gap-2 px-3 py-2 bg-bg-primary rounded-sm border border-border-default/50">
          <div class="w-1.5 h-1.5 rounded-full bg-accent-warning shrink-0"></div>
          <span class="text-data-sm text-text-primary font-mono">{corr}</span>
        </div>
      {/each}
    </div>
  {:else}
    <div class="flex items-center justify-center h-16 text-text-dim text-data-sm">
      No correlations detected
    </div>
  {/if}
</div>
