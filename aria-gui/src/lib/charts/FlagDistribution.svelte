<script lang="ts">
  import type { Flag } from '../types'
  import { countByType, fraudTypeColor } from '../utils'

  interface Props {
    flags: Flag[]
    class?: string
  }

  let { flags, class: className = '' }: Props = $props()
  let counts = $derived(countByType(flags))
  let entries = $derived(Object.entries(counts))
  let maxCount = $derived(Math.max(...Object.values(counts), 1))
</script>

<div class={className}>
  <div class="text-label text-text-muted mb-3">FLAGS BY FRAUD TYPE</div>
  <div class="space-y-3">
    {#each entries as [type, count]}
      <div class="flex items-center gap-3">
        <span class="w-3 h-3 rounded-sm shrink-0" style="background: {fraudTypeColor(type as any)}"></span>
        <span class="text-data-base text-text-primary flex-1 font-mono">{type}</span>
        <span class="text-data-lg font-mono" style="color: {fraudTypeColor(type as any)}">{count}</span>
        <div class="flex-1 h-2 bg-bg-primary rounded-sm overflow-hidden max-w-[120px]">
          <div
            class="h-full rounded-sm transition-all duration-long"
            style="width: {(count / maxCount) * 100}%; background: {fraudTypeColor(type as any)}"
          ></div>
        </div>
      </div>
    {/each}
  </div>
</div>
