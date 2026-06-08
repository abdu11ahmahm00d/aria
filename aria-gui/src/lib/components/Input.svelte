<script lang="ts">
  import { cn } from '../utils'

  interface Props {
    label?: string
    value?: string
    placeholder?: string
    type?: string
    disabled?: boolean
    class?: string
    onchange?: (e: Event) => void
  }

  let { label = '', value = '', placeholder = '', type = 'text', disabled = false, class: className = '', onchange }: Props = $props()
</script>

<div class={cn('flex flex-col gap-1.5', className)}>
  {#if label}
    <span class="text-label text-text-muted">{label}</span>
  {/if}
  <input
    {type}
    {placeholder}
    {disabled}
    bind:value
    {onchange}
    class="w-full bg-bg-deep border border-border-default rounded-lg px-3 py-2 text-data-base text-text-primary placeholder:text-text-dim
           focus:outline-none focus:border-teal/50 focus:ring-1 focus:ring-teal/20
           disabled:opacity-40 disabled:pointer-events-none transition-all duration-200"
  />
</div>
