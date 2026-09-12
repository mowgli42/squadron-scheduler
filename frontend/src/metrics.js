/** Client-side copy of backend/metrics.py so the board can compute locally. */

export const STAGE_ORDER = ['planned', 'tail', 'loadout', 'crewed', 'crew-ready', 'airborne']

export const STAGE_LABELS = {
  planned: 'Planned',
  tail: 'Tail assigned',
  loadout: 'Loadout set',
  crewed: 'Crew filled',
  'crew-ready': 'Crew-ready',
  airborne: 'Airborne',
}

function hasRole(sortie, role) {
  return (sortie.crew || []).some(c => c.position === role)
}

export function blockers(sortie) {
  const out = []
  if (!sortie.tail) out.push('missing tail')
  if (!sortie.loadout) out.push('missing loadout')
  if (!hasRole(sortie, 'pilot')) out.push('missing pilot')
  if (!hasRole(sortie, 'wso')) out.push('missing WSO')
  return out
}

export function stageOf(sortie) {
  if (sortie.status === 'airborne') return 'airborne'
  if (sortie.status === 'crew-ready') return 'crew-ready'
  if (hasRole(sortie, 'pilot') && hasRole(sortie, 'wso')) return 'crewed'
  if (sortie.loadout) return 'loadout'
  if (sortie.tail) return 'tail'
  return 'planned'
}

export function annotate(sortie) {
  const s = { ...sortie }
  s.stage = stageOf(s)
  s.blockers = blockers(s)
  s.executable = s.stage === 'crew-ready' || s.stage === 'airborne'
  return s
}

export function summarize(sorties, aircraft = []) {
  const rows = sorties.map(annotate)
  const total = rows.length
  const funnel = Object.fromEntries(STAGE_ORDER.map(k => [k, 0]))
  for (const r of rows) funnel[r.stage] += 1
  const tails = rows.filter(r => r.tail).length
  const loads = rows.filter(r => r.loadout).length
  const crewed = rows.filter(r => ['crewed', 'crew-ready', 'airborne'].includes(r.stage)).length
  const executable = rows.filter(r => r.executable).length
  const gap = {}
  for (const r of rows) {
    if (r.blockers.length) gap[r.blockers[0]] = (gap[r.blockers[0]] || 0) + 1
  }
  const next = Object.keys(gap).length
    ? Object.entries(gap).sort((a, b) => b[1] - a[1])[0][0]
    : 'all lines executable'
  return {
    sorties_total: total,
    executable,
    executable_pct: total ? Math.round((100 * executable) / total) : 0,
    tails_assigned: tails,
    loadouts_applied: loads,
    crew_complete: crewed,
    airborne: funnel.airborne,
    aircraft_available: aircraft.filter(a => a.status === 'MC' || a.status === 'PMC').length,
    aircraft_total: aircraft.length,
    funnel,
    next_action: next,
    exceptions: rows
      .filter(r => r.blockers.length && r.stage !== 'crew-ready' && r.stage !== 'airborne')
      .map(r => ({
        id: r.id,
        mission: r.mission,
        takeoff: r.takeoff,
        stage: r.stage,
        blockers: r.blockers,
      })),
  }
}
