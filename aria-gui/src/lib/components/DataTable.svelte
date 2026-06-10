<script lang="ts">
  import { cn } from '../utils'

  interface Column {
    key: string
    label: string
    mono?: boolean
    numeric?: boolean
    width?: string
    render?: (value: unknown, row: Record<string, unknown>) => string
  }

  interface Props {
    columns: Column[]
    data: Record<string, unknown>[]
    class?: string
  }

  let { columns, data, class: className = '' }: Props = $props()
</script>

<div class={cn('border border-border-default rounded-xl overflow-hidden', className)}>
  <div class="overflow-x-auto scrollbar-thin">
    <table class="w-full border-collapse">
      <thead>
        <tr class="bg-bg-deep border-b border-border-default">
          {#each columns as col}
            <th
              class={cn(
                'h-8 px-3 text-label text-text-dim font-medium whitespace-nowrap',
                col.mono && 'font-mono tracking-normal normal-case',
                col.numeric && 'text-right'
              )}
              style={col.width ? `width: ${col.width}` : ''}
            >
              {col.label}
            </th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each data as row, i (i)}
          <tr
            class="transition-all duration-150 cursor-default hover:bg-white/[0.03]"
            class:bg-bg-surface-hover={i % 2 === 1}
          >
            {#each columns as col}
              <td
                class={cn(
                  'h-8 px-3 text-data-base text-text-primary border-b border-border-default/50 whitespace-nowrap',
                  col.mono && 'font-mono',
                  col.numeric && 'text-right tabular-nums'
                )}
              >
                {#if col.render}{@html col.render(row[col.key], row)}{:else}{String(row[col.key] ?? '—')}{/if}
              </td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
  {#if data.length === 0}
    <div class="flex items-center justify-center h-24 text-text-dim text-data-base">
      No data
    </div>
  {/if}
</div>
