<script lang="ts">
  import { flags } from '../lib/stores'
  import { fraudTypeColor, formatTimestamp } from '../lib/utils'
  import Card from '../lib/components/Card.svelte'
  import Badge from '../lib/components/Badge.svelte'
  import Drawer from '../lib/components/Drawer.svelte'
  import type { Flag } from '../lib/types'

  let f = $derived($flags)

  let studentMap = $derived(() => {
    const map = new Map<string, Flag[]>()
    for (const flag of f) {
      const parts = flag.record_id?.split('_') || []
      for (const part of parts) {
        if (part.startsWith('STU')) {
          if (!map.has(part)) map.set(part, [])
          map.get(part)!.push(flag)
        }
      }
    }
    return map
  })

  let students = $derived(
    [...studentMap().entries()]
      .map(([id, fl]) => ({ id, flags: fl, types: [...new Set(fl.map(x => x.fraud_type))] }))
      .sort((a, b) => b.flags.length - a.flags.length)
  )

  let selectedStudent = $state<{ id: string; flags: Flag[]; types: string[] } | null>(null)
</script>

<div class="p-6 pt-16 md:pt-6 space-y-6">
  <div>
    <h1 class="text-2xl font-bold"><span class="text-gradient-purple">Students</span></h1>
    <p class="text-text-muted text-data-base mt-1">{students.length} student{students.length !== 1 ? 's' : ''} flagged</p>
  </div>

  <div class="grid grid-cols-2 gap-4">
    {#each students as student}
      <Card hover={true} accent={student.flags.length >= 3 ? 'critical' : student.flags.length >= 2 ? 'warning' : 'healthy'}>
        <button
          onclick={() => selectedStudent = student}
          class="w-full text-left cursor-pointer"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="font-mono text-data-base text-text-primary font-semibold">{student.id}</span>
            <Badge variant={student.flags.length >= 3 ? 'critical' : student.flags.length >= 2 ? 'warning' : 'healthy'}>
              {student.flags.length} flag{student.flags.length !== 1 ? 's' : ''}
            </Badge>
          </div>
          <div class="flex flex-wrap gap-1.5">
            {#each student.types as type}
              <span class="px-2 py-0.5 rounded-md text-data-sm font-medium" style="background: {fraudTypeColor(type as any)}20; color: {fraudTypeColor(type as any)}">{type}</span>
            {/each}
          </div>
        </button>
      </Card>
    {/each}
  </div>

  {#if students.length === 0}
    <div class="flex items-center justify-center h-32 border border-border-default rounded-xl bg-bg-surface">
      <span class="text-text-dim text-data-base">No students flagged. Run the pipeline first.</span>
    </div>
  {/if}

  <Drawer
    open={selectedStudent !== null}
    title={selectedStudent?.id || ''}
    onclose={() => selectedStudent = null}
  >
    {#if selectedStudent}
      <div class="space-y-4">
        {#each selectedStudent.flags as flag}
          <Card>
            <div class="flex items-center gap-2 mb-2">
              <span class="w-2 h-2 rounded-full shrink-0" style="background: {fraudTypeColor(flag.fraud_type)}"></span>
              <span class="text-data-base font-semibold text-text-primary">{flag.fraud_type}</span>
              <Badge>{(flag.confidence * 100).toFixed(0)}%</Badge>
            </div>
            <p class="font-mono text-data-sm text-text-muted mb-1">{flag.reason}</p>
            <pre class="font-mono text-data-sm text-text-dim bg-bg-deep p-2 rounded-lg overflow-x-auto">{JSON.stringify(flag.evidence, null, 2)}</pre>
          </Card>
        {/each}
      </div>
    {/if}
  </Drawer>
</div>
