<script lang="ts">
  import { cn } from '../utils'

  interface Props {
    accent?: 'healthy' | 'warning' | 'critical' | 'none'
    hover?: boolean
    class?: string
    children?: import('svelte').Snippet
  }

  let { accent = 'none', hover = false, class: className = '', children }: Props = $props()
</script>

<div
  class={cn(
    'relative bg-bg-surface border border-border-default rounded-xl p-4 overflow-hidden',
    hover && 'transition-all duration-200 hover:bg-bg-surface-hover hover:border-teal/20 hover:shadow-lg hover:shadow-teal-glow/5',
    className
  )}
>
  {#if accent !== 'none'}
    <div
      class="absolute top-0 left-0 w-full h-0.5"
      class:bg-teal={accent === 'healthy'}
      class:bg-amber-500={accent === 'warning'}
      class:bg-red-500={accent === 'critical'}
    ></div>
  {/if}
  {@render children?.()}
</div>
