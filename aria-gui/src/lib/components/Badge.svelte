<script lang="ts">
  import { cn } from '../utils'

  interface Props {
    variant?: 'healthy' | 'warning' | 'critical' | 'info'
    class?: string
    children?: import('svelte').Snippet
  }

  let { variant = 'info', class: className = '', children }: Props = $props()
</script>

<span
  class={cn(
    'inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-data-sm font-medium',
    variant === 'healthy' && 'bg-teal/10 text-teal',
    variant === 'warning' && 'bg-amber-500/10 text-amber-400',
    variant === 'critical' && 'bg-red-500/10 text-red-400',
    variant === 'info' && 'bg-sky/10 text-sky',
    className
  )}
>
  {@render children?.()}
</span>
