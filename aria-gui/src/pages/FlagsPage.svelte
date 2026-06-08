<script lang="ts">
  import { flags } from '../lib/stores'
  import { fraudTypeColor } from '../lib/utils'
  import DataTable from '../lib/components/DataTable.svelte'
  import type { Flag } from '../lib/types'
  import { Search } from '@lucide/svelte'

  let f = $derived($flags)
  let searchQuery = $state('')
  let selectedType = $state<string>('all')

  let filtered = $derived(
    f.filter(flag => {
      if (selectedType !== 'all' && flag.fraud_type !== selectedType) return false
      if (searchQuery && !flag.record_id?.toLowerCase().includes(searchQuery.toLowerCase())) return false
      return true
    })
  )

  let types = $derived(['all', ...new Set(f.map(x => x.fraud_type))])

  const columns = [
    {
      key: 'fraud_type', label: 'TYPE', width: '160px',
      render: (v: unknown) => `<div class="flex items-center gap-2"><span class="w-2 h-2 rounded-full shrink-0" style="background: ${fraudTypeColor(v as any)}"></span><span>${v}</span></div>`
    },
    { key: 'record_id', label: 'RECORD', mono: true, width: '200px' },
    { key: 'reason', label: 'REASON', width: 'auto' },
    {
      key: 'confidence', label: 'CONFIDENCE', numeric: true, mono: true, width: '120px',
      render: (v: unknown) => `${((v as number) * 100).toFixed(0)}%`
    },
  ]
</script>

<div class="p-6 pt-16 md:pt-6 space-y-4">
  <div>
    <h1 class="text-2xl font-bold"><span class="text-gradient-purple">Flags</span></h1>
    <p class="text-text-muted text-data-base mt-1">{f.length} total flag{f.length !== 1 ? 's' : ''}</p>
  </div>

  <div class="flex items-center gap-3">
    <div class="relative flex-1 max-w-sm">
      <Search size={14} class="absolute left-3 top-1/2 -translate-y-1/2 text-text-dim" />
      <input
        type="text"
        placeholder="Search by record ID..."
        bind:value={searchQuery}
        class="w-full bg-bg-surface border border-border-default rounded-lg pl-9 pr-3 py-2 text-data-base text-text-primary placeholder:text-text-dim focus:outline-none focus:border-teal transition-all duration-200"
      />
    </div>
    <div class="flex gap-1">
      {#each types as type}
        <button
          onclick={() => selectedType = type}
          class="px-3 py-1.5 rounded-lg text-data-sm font-medium transition-all duration-200 cursor-pointer
            {selectedType === type ? 'bg-teal/10 text-teal' : 'text-text-muted hover:text-text-primary hover:bg-white/5'}"
        >
          {type === 'all' ? 'All' : type}
        </button>
      {/each}
    </div>
  </div>

  {#if filtered.length > 0}
    <DataTable {columns} data={filtered as unknown as Record<string, unknown>[]} />
  {:else}
    <div class="flex items-center justify-center h-32 border border-border-default rounded-xl bg-bg-surface">
      <span class="text-text-dim text-data-base">
        {#if f.length === 0}No flags generated yet. Run the pipeline first.{:else}No flags match your filter.{/if}
      </span>
    </div>
  {/if}
</div>
