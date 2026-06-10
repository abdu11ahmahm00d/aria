<script lang="ts">
  import { cn } from '../utils'

  let { variant = 'primary', size = 'md', disabled = false, class: className = '', children }: {
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
    size?: 'sm' | 'md' | 'lg'
    disabled?: boolean
    class?: string
    children?: import('svelte').Snippet
  } = $props()
</script>

<button
  disabled={disabled}
  class={cn(
    'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all duration-200 cursor-pointer select-none',
    'disabled:opacity-40 disabled:pointer-events-none',
    variant === 'primary' && 'bg-gradient-to-r from-teal to-purple text-white hover:from-teal/90 hover:to-purple/90 hover:shadow-lg hover:shadow-purple-glow',
    variant === 'secondary' && 'border border-border-default bg-transparent text-text-primary hover:bg-white/5 hover:border-teal/30',
    variant === 'ghost' && 'bg-transparent text-text-muted hover:text-text-primary hover:bg-white/5',
    variant === 'danger' && 'bg-red-500 text-white hover:bg-red-600',
    size === 'sm' && 'px-3 py-1 text-data-sm',
    size === 'md' && 'px-4 py-2 text-data-base',
    size === 'lg' && 'px-6 py-3 text-data-base',
    className
  )}
>
  {@render children?.()}
</button>
