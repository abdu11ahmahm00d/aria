<script lang="ts">
  import { cn } from '../utils'

  interface Tile {
    label: string
    value: string
    trend?: 'up' | 'down' | 'neutral'
    color?: string
  }

  interface Props {
    tiles: Tile[]
    class?: string
  }

  let { tiles, class: className = '' }: Props = $props()
</script>

<div class={cn('grid grid-cols-4 gap-px bg-border-default rounded-xl overflow-hidden', className)}>
  {#each tiles as tile}
    <div class="bg-bg-surface p-4 flex flex-col gap-2">
      <span class="text-label text-text-muted">{tile.label}</span>
      <div class="flex items-center gap-3">
        <span class="text-data-lg" style={tile.color ? `color: ${tile.color}` : ''}>{tile.value}</span>
        {#if tile.trend}
          <span
            class="text-data-sm font-medium"
            class:text-teal={tile.trend === 'up'}
            class:text-red-400={tile.trend === 'down'}
            class:text-text-muted={tile.trend === 'neutral'}
          >
            {tile.trend === 'up' ? '▲' : tile.trend === 'down' ? '▼' : '—'}
          </span>
        {/if}
      </div>
      <div class="flex gap-0.5 h-6 items-end">
        {#each Array(12) as _, i}
          <div
            class="flex-1 rounded-sm transition-all duration-300"
            style="height: {20 + Math.random() * 60}%; background: {tile.color || 'var(--color-teal)'}; opacity: {0.3 + Math.random() * 0.5}"
          ></div>
        {/each}
      </div>
    </div>
  {/each}
</div>
