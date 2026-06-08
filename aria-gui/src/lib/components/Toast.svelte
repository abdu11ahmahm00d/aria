<script lang="ts">
  import { cn } from '../utils'
  import { X } from '@lucide/svelte'
  import { onMount } from 'svelte'

  interface Props {
    message: string
    type?: 'success' | 'error' | 'info'
    duration?: number
    ondismiss?: () => void
  }

  let { message, type = 'info', duration = 4000, ondismiss }: Props = $props()
  let visible = $state(true)

  onMount(() => {
    const timer = setTimeout(() => {
      visible = false
      setTimeout(() => ondismiss?.(), 300)
    }, duration)
    return () => clearTimeout(timer)
  })
</script>

{#if visible}
  <div
    class={cn(
      'fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-xl border shadow-lg animate-fade-in-up min-w-[300px]',
      type === 'success' && 'bg-teal/10 border-teal/30 text-teal shadow-teal-glow/10',
      type === 'error' && 'bg-red-500/10 border-red-500/30 text-red-400',
      type === 'info' && 'bg-bg-surface border-border-default text-text-primary'
    )}
  >
    <span class="text-data-base flex-1">{message}</span>
    <button onclick={() => { visible = false; ondismiss?.() }} class="text-text-muted hover:text-text-primary transition-all duration-200 cursor-pointer hover:scale-110">
      <X size={14} />
    </button>
  </div>
{/if}
