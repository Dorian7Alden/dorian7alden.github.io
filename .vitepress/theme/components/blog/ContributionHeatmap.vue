<script setup lang="ts">
import { computed } from 'vue'

interface DayCell {
  date: string
  level: 0 | 1 | 2 | 3 | 4
  count: number
}

const DAY_LABELS = ['', 'Mon', '', 'Wed', '', 'Fri', '']
const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

function generateMockData(): DayCell[][] {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const todayStr = today.toISOString().slice(0, 10)
  const seed = todayStr.split('-').reduce((acc, n) => acc + parseInt(n, 10), 0)
  const random = seededRandom(seed)
  // Start from 52 weeks ago, aligned to Sunday
  const startDate = new Date(today)
  startDate.setDate(today.getDate() - today.getDay() - 51 * 7)
  // today.getDay() gives day of week (0=Sun). Go back to previous Sunday, then back 51 more weeks = 52 total weeks

  const weeks: DayCell[][] = []
  const current = new Date(startDate)

  for (let w = 0; w < 52; w++) {
    const week: DayCell[] = []
    for (let d = 0; d < 7; d++) {
      const dateStr = current.toISOString().slice(0, 10)
      const dayOfWeek = current.getDay()

      // Weighted random: weekdays more active, weekends less
      let baseProbability = dayOfWeek >= 1 && dayOfWeek <= 5 ? 0.5 : 0.2

      // Don't generate future contributions
      if (current > today) {
        week.push({ date: dateStr, level: 0, count: 0 })
      } else {
        const rand = random()
        let level: 0 | 1 | 2 | 3 | 4
        let count: number
        if (rand < 1 - baseProbability) {
          level = 0; count = 0
        } else if (rand < baseProbability + 0.18) {
          level = 1; count = Math.floor(random() * 4) + 1
        } else if (rand < baseProbability + 0.30) {
          level = 2; count = Math.floor(random() * 6) + 5
        } else if (rand < baseProbability + 0.39) {
          level = 3; count = Math.floor(random() * 10) + 11
        } else {
          level = 4; count = Math.floor(random() * 10) + 21
        }
        week.push({ date: dateStr, level, count })
      }
      current.setDate(current.getDate() + 1)
    }
    weeks.push(week)
  }
  return weeks
}

function seededRandom(seed: number): () => number {
  let s = seed
  return () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646 }
}

const weeks = generateMockData()

const monthLabels = computed(() => {
  const labels: { label: string; col: number }[] = []
  let lastMonth = -1
  weeks.forEach((week, colIndex) => {
    const firstDay = week[0]
    if (!firstDay) return
    const month = parseInt(firstDay.date.slice(5, 7), 10) - 1
    if (month !== lastMonth) {
      labels.push({ label: MONTH_LABELS[month], col: colIndex })
      lastMonth = month
    }
  })
  return labels
})

function getLevelColor(level: number): string {
  return `var(--heatmap-level-${level})`
}
</script>

<template>
  <div class="heatmap">
    <div class="heatmap-header">
      <span class="heatmap-title">Contributions</span>
    </div>
    <div class="heatmap-scroll">
      <div class="heatmap-grid-wrapper">
        <div class="heatmap-months">
          <span
            v-for="(m, i) in monthLabels"
            :key="i"
            class="heatmap-month"
            :style="{ gridColumn: m.col + 2 }"
          >{{ m.label }}</span>
        </div>
        <div class="heatmap-body">
          <div class="heatmap-day-labels">
            <span v-for="(label, i) in DAY_LABELS" :key="i" class="heatmap-day-label">{{ label }}</span>
          </div>
          <div class="heatmap-grid">
            <div
              v-for="(week, wi) in weeks"
              :key="wi"
              class="heatmap-week"
            >
              <div
                v-for="(day, di) in week"
                :key="di"
                class="heatmap-cell"
                :style="{ backgroundColor: getLevelColor(day.level) }"
                :title="`${day.date}: ${day.count} contributions`"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.heatmap {
  margin-top: 16px;
}

.heatmap-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.heatmap-title {
  font-size: 0.82rem;
  font-weight: 650;
  color: var(--vp-c-text-2);
}

.heatmap-scroll {
  overflow-x: auto;
  padding-bottom: 4px;
}

.heatmap-grid-wrapper {
  display: inline-block;
  min-width: 720px;
}

.heatmap-months {
  display: grid;
  grid-template-columns: 28px repeat(52, 11px);
  gap: 3px;
  margin-bottom: 2px;
  padding-left: 0;
}

.heatmap-month {
  font-size: 0.68rem;
  color: var(--vp-c-text-3);
  line-height: 1;
}

.heatmap-body {
  display: flex;
  gap: 0;
}

.heatmap-day-labels {
  display: grid;
  grid-template-rows: repeat(7, 11px);
  gap: 3px;
  margin-right: 6px;
  padding-top: 0;
}

.heatmap-day-label {
  font-size: 0.65rem;
  color: var(--vp-c-text-3);
  line-height: 11px;
}

.heatmap-grid {
  display: flex;
  gap: 3px;
}

.heatmap-week {
  display: grid;
  grid-template-rows: repeat(7, 11px);
  gap: 3px;
}

.heatmap-cell {
  width: 11px;
  height: 11px;
  border-radius: 2px;
  transition: transform 0.15s ease;
}

.heatmap-cell:hover {
  transform: scale(1.4);
  outline: 1px solid var(--vp-c-border);
}

/* Light mode levels */
.heatmap-cell { --heatmap-level-0: #ebedf0; }
.heatmap-cell { --heatmap-level-1: #9be9a8; }
.heatmap-cell { --heatmap-level-2: #40c463; }
.heatmap-cell { --heatmap-level-3: #30a14e; }
.heatmap-cell { --heatmap-level-4: #216e39; }

/* Dark mode levels */
.dark .heatmap-cell { --heatmap-level-0: #161b22; }
.dark .heatmap-cell { --heatmap-level-1: #0e4429; }
.dark .heatmap-cell { --heatmap-level-2: #006d32; }
.dark .heatmap-cell { --heatmap-level-3: #26a641; }
.dark .heatmap-cell { --heatmap-level-4: #39d353; }

@media (max-width: 768px) {
  .heatmap-grid-wrapper {
    min-width: 600px;
  }
}
</style>
