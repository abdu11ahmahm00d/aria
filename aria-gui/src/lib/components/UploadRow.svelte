<script lang="ts">
  import { cn } from '../utils'
  import { Upload, Check } from '@lucide/svelte'
  import type { UploadedFile } from '../uploads'

  interface Props {
    label: string
    file: UploadedFile | null
    onselect: () => void
  }

  let { label, file, onselect }: Props = $props()
</script>

<button
  onclick={onselect}
  class={cn(
    'w-full flex items-center gap-3 px-4 py-3 rounded-xl border transition-all duration-200 cursor-pointer text-left',
    file
      ? 'bg-teal/5 border-teal/30 hover:bg-teal/10'
      : 'bg-white/[0.02] border-border-default hover:border-teal/20 hover:bg-white/5'
  )}
>
  <span class="shrink-0 {file ? 'text-teal' : 'text-text-dim'}">
    {#if file}
      <Check size={18} />
    {:else}
      <Upload size={18} />
    {/if}
  </span>
  <span class="flex-1 {file ? 'text-teal' : 'text-text-muted'} text-data-base font-medium">
    {file ? `${file.meta.name} (${file.meta.rows} rows)` : label}
  </span>
  <span class="text-data-sm {file ? 'text-teal' : 'text-text-dim'}">{file ? 'Change' : 'Browse'}</span>
</button>
