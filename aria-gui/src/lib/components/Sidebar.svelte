<script lang="ts">
  import { cn } from '../utils'
  import { navItems, currentView, totalFlags } from '../stores'
  import {
    LayoutDashboard, FlagTriangleRight, BookOpen, Users, Play
  } from '@lucide/svelte'

  let view = $derived($currentView)
  let total = $derived($totalFlags)

  const accentFor = (id: string) => {
    switch (id) {
      case 'dashboard': return 'teal'
      case 'flags': return 'purple'
      case 'courses': return 'sky'
      case 'students': return 'purple'
      case 'run': return 'teal'
      default: return 'teal'
    }
  }

  const colorVar = (c: string) =>
    c === 'teal' ? 'var(--color-teal)' :
    c === 'purple' ? 'var(--color-purple)' :
    'var(--color-sky)'

  const iconFor = (id: string, size = 18) => {
    switch (id) {
      case 'dashboard': return LayoutDashboard
      case 'flags': return FlagTriangleRight
      case 'courses': return BookOpen
      case 'students': return Users
      case 'run': return Play
      default: return LayoutDashboard
    }
  }
</script>

<aside class="h-full w-60 glass border-r border-border-teal flex flex-col">
  <!-- branding -->
  <div class="h-16 flex items-center gap-3 px-5 border-b border-border-teal/30 shrink-0">
    <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-teal to-purple flex items-center justify-center shadow-lg shadow-purple-glow">
      <span class="text-white text-sm font-bold font-mono">A</span>
    </div>
    <div>
      <span class="text-data-base font-semibold text-gradient">ARIA</span>
      <span class="text-label text-text-dim block">Integrity Auditor</span>
    </div>
  </div>

  <!-- nav items -->
  <nav class="flex-1 py-4 px-3 space-y-1.5 overflow-y-auto">
    {#each navItems as item, i}
      {@const accent = accentFor(item.id)}
      {@const color = colorVar(accent)}
      {@const Icon = iconFor(item.id)}
      <button
        onclick={() => currentView.set(item.id)}
        class={cn(
          'w-full flex items-center gap-3.5 px-4 py-3 rounded-xl text-data-base font-medium transition-all duration-200 cursor-pointer text-left group',
          'hover:bg-white/5',
          view === item.id
            ? 'bg-white/10 text-white shadow-sm'
            : 'text-text-muted hover:text-text-primary'
        )}
        style={view === item.id ? `box-shadow: inset 0 0 0 1px ${color}40, 0 0 20px ${color}10` : ''}
      >
        <!-- accent dot -->
        <span
          class="w-2 h-2 rounded-full shrink-0 transition-all duration-200"
          class:shadow-lg={view === item.id}
          class:opacity-40={view !== item.id}
          class:opacity-100={view === item.id}
          style="background: {color}; box-shadow: {view === item.id ? `0 0 8px ${color}` : 'none'}"
        ></span>

        <!-- icon -->
        <span class="shrink-0 transition-transform duration-200 group-hover:scale-110" style="color: {view === item.id ? color : ''}">
          <Icon size={18} />
        </span>

        <!-- label -->
        <span class="flex-1">{item.label}</span>

        <!-- badge for flags -->
        {#if item.id === 'flags' && total > 0}
          <span
            class="px-2 py-0.5 rounded-md text-data-sm font-bold"
            style="background: {color}20; color: {color}"
          >
            {total}
          </span>
        {/if}

        <!-- active indicator bar -->
        {#if view === item.id}
          <span class="w-1 h-5 rounded-full shrink-0" style="background: {color}; box-shadow: 0 0 8px {color}"></span>
        {/if}
      </button>
    {/each}
  </nav>

  <!-- status footer -->
  <div class="px-5 py-4 border-t border-border-teal/30 shrink-0">
    <div class="flex items-center gap-3">
      <span class="relative flex w-2.5 h-2.5">
        <span class="animate-ping absolute inset-0 rounded-full bg-teal opacity-40"></span>
        <span class="relative rounded-full w-2.5 h-2.5 bg-teal"></span>
      </span>
      <span class="text-data-sm text-text-dim">Pipeline Ready</span>
    </div>
  </div>
</aside>
