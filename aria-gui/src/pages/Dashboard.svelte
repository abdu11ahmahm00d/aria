<script lang="ts">
  import { flags, totalFlags, severity, report, isRunning } from '../lib/stores'
  import { severityColor } from '../lib/utils'
  import Card from '../lib/components/Card.svelte'
  import DataRibbon from '../lib/components/DataRibbon.svelte'
  import Badge from '../lib/components/Badge.svelte'
  import FlagDistribution from '../lib/charts/FlagDistribution.svelte'
  import CorrelationGraph from '../lib/charts/CorrelationGraph.svelte'

  let f = $derived($flags)
  let total = $derived($totalFlags)
  let sev = $derived($severity)
  let rep = $derived($report)

  let tiles = $derived([
    { label: 'Total Flags', value: String(total), trend: total > 0 ? 'up' as const : 'neutral' as const, color: severityColor(sev) },
    { label: 'Courses Flagged', value: String(new Set(f.map(x => x.record_id?.split('_')[0]).filter(Boolean)).size), color: '#a855f7' },
    { label: 'Students Flagged', value: String(new Set(f.flatMap(x => [...(x.record_id?.match(/STU\d+/g) || [])])).size || '—'), color: '#38bdf8' },
    { label: 'Severity', value: sev, color: severityColor(sev) },
  ])
</script>

<div class="p-6 pt-16 md:pt-6 space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-2xl font-bold">
        <span class="text-gradient">Dashboard</span>
      </h1>
      <p class="text-text-muted text-data-base mt-1">Academic Integrity and OBE Analytics Dashboard</p>
    </div>
    <div class="flex items-center gap-3">
      {#if $isRunning}
        <Badge variant="warning">Pipeline Running...</Badge>
      {:else}
        <Badge variant={sev === 'HIGH' ? 'critical' : sev === 'MEDIUM' ? 'warning' : 'healthy'}>{sev}</Badge>
      {/if}
    </div>
  </div>

  {#if f.length === 0 && !$isRunning}
    <Card class="py-12 flex flex-col items-center justify-center gap-4">
      <span class="text-data-lg text-text-dim">No Data</span>
      <p class="text-data-base text-text-muted text-center max-w-md">
        Run the ARIA pipeline to generate fraud detection flags and reports.
      </p>
    </Card>
  {:else}
    <DataRibbon {tiles} />

    <div class="grid grid-cols-5 gap-4">
      <div class="col-span-3">
        <Card>
          <FlagDistribution flags={f} />
        </Card>
      </div>
      <div class="col-span-2">
        <Card>
          <CorrelationGraph flags={f} />
        </Card>
      </div>
    </div>

    {#if rep}
      <Card>
        <div class="text-label text-text-muted mb-3">REPORT PREVIEW</div>
        <pre class="font-mono text-data-sm text-text-muted whitespace-pre-wrap max-h-64 overflow-y-auto scrollbar-thin">{rep.slice(0, 2000)}</pre>
      </Card>
    {/if}
  {/if}
</div>
