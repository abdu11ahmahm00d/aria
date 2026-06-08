<script lang="ts">
  import { cn } from '../utils'
  import { X } from '@lucide/svelte'

  interface Props {
    open: boolean
    title?: string
    onclose?: () => void
    children?: import('svelte').Snippet
    class?: string
  }

  let { open, title = '', onclose, children, class: className = '' }: Props = $props()
</script>

{#if open}
  <div class="fixed inset-0 z-50 flex justify-end">
    <div
      class="absolute inset-0 bg-black/70 backdrop-blur-sm"
      role="button"
      tabindex="0"
      onclick={onclose}
      onkeydown={(e) => { if (e.key === 'Escape' || e.key === ' ') { e.preventDefault(); onclose?.() } }}
    ></div>
    <div
      class={cn(
        'relative w-[480px] max-w-[90vw] h-full bg-bg-surface border-l border-border-teal animate-slide-in overflow-y-auto scrollbar-thin',
        className
      )}
    >
      <div class="sticky top-0 z-10 bg-bg-surface border-b border-border-teal/30 px-5 py-3 flex items-center justify-between">
        <h2 class="text-data-base font-semibold text-gradient">{title}</h2>
        <button onclick={onclose} class="text-text-muted hover:text-text-primary transition-all duration-200 cursor-pointer p-1 hover:scale-110">
          <X size={16} />
        </button>
      </div>
      <div class="p-5">
        {@render children?.()}
      </div>
    </div>
  </div>
{/if}
