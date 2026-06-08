<script lang="ts">
  import { flags } from '../lib/stores'
  import { groupBy, severityColor, fraudTypeColor } from '../lib/utils'
  import Card from '../lib/components/Card.svelte'
  import Badge from '../lib/components/Badge.svelte'
  import type { Flag, Severity } from '../lib/types'

  let f = $derived($flags)
  let courseGroups = $derived(groupBy(f, (flag: Flag) => flag.record_id?.split('_')[0] || 'unknown'))

  function courseSeverity(courseFlags: Flag[]): Severity {
    const t = courseFlags.length
    const types = new Set(courseFlags.map(x => x.fraud_type))
    if (t >= 3 || (types.has('Grade Inflation') && types.has('Submission Clustering'))) return 'HIGH'
    if (t >= 2) return 'MEDIUM'
    return 'LOW'
  }

  let courseList = $derived(
    Object.entries(courseGroups)
      .map(([id, cf]) => ({ id, flags: cf, severity: courseSeverity(cf), types: [...new Set(cf.map(x => x.fraud_type))] }))
      .sort((a, b) => b.flags.length - a.flags.length)
  )
</script>

<div class="p-6 pt-16 md:pt-6 space-y-6">
  <div>
    <h1 class="text-2xl font-bold"><span class="text-gradient">Courses</span></h1>
    <p class="text-text-muted text-data-base mt-1">{courseList.length} course{courseList.length !== 1 ? 's' : ''} flagged</p>
  </div>

  <div class="grid grid-cols-3 gap-4 auto-rows-min">
    {#each courseList as course}
      <Card
        accent={course.severity === 'HIGH' ? 'critical' : course.severity === 'MEDIUM' ? 'warning' : 'healthy'}
        hover={true}
        class="cursor-pointer"
      >
        <div class="flex items-start justify-between mb-3">
          <div>
            <span class="font-mono text-data-base text-text-primary font-semibold">{course.id}</span>
          </div>
          <Badge
            variant={course.severity === 'HIGH' ? 'critical' : course.severity === 'MEDIUM' ? 'warning' : 'healthy'}
          >
            {course.flags.length} flag{course.flags.length !== 1 ? 's' : ''}
          </Badge>
        </div>
        <div class="flex flex-wrap gap-1.5">
          {#each course.types as type}
            <span
              class="px-2 py-0.5 rounded-md text-data-sm font-medium"
              style="background: {fraudTypeColor(type as any)}20; color: {fraudTypeColor(type as any)}"
            >
              {type}
            </span>
          {/each}
        </div>
      </Card>
    {/each}
  </div>

  {#if courseList.length === 0}
    <div class="flex items-center justify-center h-32 border border-border-default rounded-xl bg-bg-surface">
      <span class="text-text-dim text-data-base">No courses flagged. Run the pipeline first.</span>
    </div>
  {/if}
</div>
