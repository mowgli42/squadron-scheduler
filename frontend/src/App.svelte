<script>
  import { onMount } from 'svelte'
  import { STAGE_ORDER, STAGE_LABELS, summarize } from './metrics.js'

  let sorties = $state([])
  let aircraft = $state([])
  let aircrew = $state([])
  let schedule = $state([])
  let changes = $state([])
  let metrics = $state(null)
  let error = $state('')
  let demoStages = $state([])
  let demoNote = $state('')
  let live = $state(false)

  const STATUSES = ['planned', 'crew-ready', 'airborne']

  const api = (path, opts) =>
    fetch('/api' + path, opts).then(r => {
      if (!r.ok) return r.json().then(e => Promise.reject(e.detail || r.statusText))
      return r.json()
    })

  async function load() {
    error = ''
    try {
      const [s, a, c, m, sch, ch] = await Promise.all([
        api('/sorties'),
        api('/aircraft'),
        api('/aircrew'),
        api('/metrics'),
        api('/aircraft/schedule'),
        api('/changes?limit=12'),
      ])
      live = true
      sorties = s
      aircraft = a
      aircrew = c
      schedule = sch
      changes = ch
      metrics = m || summarize(s, a)
    } catch (e) {
      live = false
      error = String(e)
    }
  }

  async function loadDemoMeta() {
    try {
      demoStages = await api('/demo/stages')
    } catch {
      /* demo optional */
    }
  }

  async function setTail(sid, tail) {
    if (!tail) return
    try {
      await api(`/sorties/${sid}/aircraft`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tail }),
      })
      await load()
    } catch (e) {
      error = String(e)
    }
  }

  async function setSpare(sid, spare_tail) {
    if (!spare_tail) return
    try {
      await api(`/sorties/${sid}/spare`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ spare_tail }),
      })
      await load()
    } catch (e) {
      error = String(e)
    }
  }

  async function setLoadout(sid, template) {
    if (!template) return
    try {
      await api(`/sorties/${sid}/loadout`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ template }),
      })
      await load()
    } catch (e) {
      error = String(e)
    }
  }

  async function setCrew(sid, position, aircrew_id) {
    if (!aircrew_id) return
    try {
      await api(`/sorties/${sid}/crew`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ position, aircrew_id: +aircrew_id }),
      })
      await load()
    } catch (e) {
      error = String(e)
    }
  }

  async function setEr(sid, signed) {
    try {
      await api(`/sorties/${sid}/er`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ signed }),
      })
      await load()
    } catch (e) {
      error = String(e)
    }
  }

  async function setStatus(sid, status) {
    if (!status) return
    try {
      await api(`/sorties/${sid}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      })
      await load()
    } catch (e) {
      error = String(e)
    }
  }

  async function applyDemo(stageId) {
    error = ''
    try {
      const r = await api(`/demo/stages/${stageId}`, { method: 'POST' })
      demoNote = r.title
      await load()
    } catch (e) {
      error = String(e)
    }
  }

  function crewName(s, pos) {
    return s.crew?.find(c => c.position === pos)?.name || '—'
  }

  function timeOf(s) {
    return s.takeoff?.slice(11, 16) || '—'
  }

  function landOf(s) {
    return s.land?.slice(11, 16) || '—'
  }

  onMount(() => {
    load()
    loadDemoMeta()
  })
</script>

<main>
  <header class="top">
    <div>
      <p class="eyebrow">Flying schedule · four-ship morning go</p>
      <h1>Can we generate today’s go?</h1>
      <p class="lede">
        Process first, then numbers, then the board.
        {#if metrics}
          Next action: <strong>{metrics.next_action}</strong>.
        {/if}
      </p>
    </div>
    <div class="top-actions">
      <span class="pulse" class:on={live}>{live ? 'Live API' : 'No API'}</span>
      <button onclick={load}>Refresh</button>
    </div>
  </header>

  {#if demoStages.length}
    <nav class="demo" aria-label="Demo build-up stages">
      <span class="demo-label">Replay process</span>
      {#each demoStages as d}
        <button type="button" onclick={() => applyDemo(d.id)}>{d.id.slice(0, 2)}</button>
      {/each}
      {#if demoNote}
        <span class="demo-note">{demoNote}</span>
      {/if}
    </nav>
  {/if}

  {#if error}
    <p class="err" role="alert">{error}</p>
  {/if}

  {#if metrics}
    <section class="metrics" aria-label="Readiness metrics">
      <article class="metric primary">
        <p class="metric-label">Executable</p>
        <p class="metric-value">{metrics.executable_pct}<span>%</span></p>
        <p class="metric-sub">{metrics.executable} of {metrics.sorties_total} lines crew-ready or airborne</p>
      </article>
      <article class="metric">
        <p class="metric-label">Tails</p>
        <p class="metric-value">{metrics.tails_assigned}<span>/{metrics.sorties_total}</span></p>
        <p class="metric-sub">{metrics.aircraft_available} MC/PMC of {metrics.aircraft_total}</p>
      </article>
      <article class="metric">
        <p class="metric-label">Spares</p>
        <p class="metric-value">{metrics.spares_assigned}<span>/{metrics.sorties_total}</span></p>
        <p class="metric-sub">backup tails named</p>
      </article>
      <article class="metric">
        <p class="metric-label">Loadouts</p>
        <p class="metric-value">{metrics.loadouts_applied}<span>/{metrics.sorties_total}</span></p>
        <p class="metric-sub">templates applied</p>
      </article>
      <article class="metric">
        <p class="metric-label">Crew / ER</p>
        <p class="metric-value">{metrics.crew_complete}<span>/{metrics.er_signed}</span></p>
        <p class="metric-sub">crewed / ER signed</p>
      </article>
      <article class="metric">
        <p class="metric-label">Airborne</p>
        <p class="metric-value">{metrics.airborne}</p>
        <p class="metric-sub">already launched</p>
      </article>
    </section>

    <section class="funnel" aria-label="Generation process">
      <h2>Generation process</h2>
      <ol>
        {#each STAGE_ORDER as key}
          <li class:hot={metrics.funnel[key] > 0}>
            <span class="count">{metrics.funnel[key]}</span>
            <span class="label">{STAGE_LABELS[key]}</span>
          </li>
        {/each}
      </ol>
    </section>

    {#if metrics.exceptions?.length}
      <section class="exceptions" aria-label="Exceptions">
        <h2>Exceptions — fix these first</h2>
        <ul>
          {#each metrics.exceptions as ex}
            <li>
              <span class="when">{ex.takeoff?.slice(11, 16)} {ex.callsign || ex.mission}</span>
              <span class="gap">{ex.blockers.join(' · ')}</span>
            </li>
          {/each}
        </ul>
      </section>
    {/if}
  {/if}

  <section class="board">
    <h2>Schedule board</h2>
    <table>
      <thead>
        <tr>
          <th>Stage</th>
          <th>Line</th>
          <th>Window</th>
          <th>Mission</th>
          <th>Primary</th>
          <th>Spare</th>
          <th>Loadout</th>
          <th>Pilot</th>
          <th>WSO</th>
          <th>ER</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {#each sorties as s}
          <tr
            class:airborne={s.status === 'airborne'}
            class:ready={s.status === 'crew-ready'}
            class:blocked={s.blockers?.length && s.status === 'planned'}
          >
            <td>
              <span class="stage stage-{s.stage}">{STAGE_LABELS[s.stage] || s.stage || '—'}</span>
            </td>
            <td>
              <strong>{s.line_number}</strong>
              <div class="muted">{s.callsign}</div>
            </td>
            <td>{timeOf(s)}–{landOf(s)}</td>
            <td>{s.mission}</td>
            <td>
              <select value={s.tail || ''} onchange={e => setTail(s.id, e.target.value)}>
                <option value="">—</option>
                {#each aircraft as a}
                  <option value={a.tail}>{a.tail} ({a.status})</option>
                {/each}
              </select>
            </td>
            <td>
              <select
                value={s.spare_tail || ''}
                onchange={e => setSpare(s.id, e.target.value)}
              >
                <option value="">—</option>
                {#each aircraft as a}
                  <option value={a.tail}>{a.tail} ({a.status})</option>
                {/each}
              </select>
            </td>
            <td>
              <select value="" onchange={e => setLoadout(s.id, e.target.value)}>
                <option value="">
                  {s.loadout
                    ? `${s.loadout_template || 'set'} · ${s.load_crew_minutes || '?'}m`
                    : 'set…'}
                </option>
                <option value="A/A">A/A</option>
                <option value="A/G">A/G</option>
                <option value="SEAD">SEAD</option>
                <option value="clean">clean</option>
              </select>
            </td>
            <td>
              <select value="" onchange={e => setCrew(s.id, 'pilot', e.target.value)}>
                <option value="">{crewName(s, 'pilot')}</option>
                {#each aircrew.filter(c => c.role === 'pilot') as c}
                  <option value={c.id}>{c.name}</option>
                {/each}
              </select>
            </td>
            <td>
              <select value="" onchange={e => setCrew(s.id, 'wso', e.target.value)}>
                <option value="">{crewName(s, 'wso')}</option>
                {#each aircrew.filter(c => c.role === 'wso') as c}
                  <option value={c.id}>{c.name}</option>
                {/each}
              </select>
            </td>
            <td>
              <label class="er">
                <input
                  type="checkbox"
                  checked={!!s.er_signed}
                  onchange={e => setEr(s.id, e.target.checked)}
                />
                ER
              </label>
            </td>
            <td>
              <select
                value={s.status || 'planned'}
                onchange={e => setStatus(s.id, e.target.value)}
              >
                {#each STATUSES as st}
                  <option value={st}>{st}</option>
                {/each}
              </select>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </section>

  {#if schedule.length}
    <section class="asset-board" aria-label="Aircraft day board">
      <h2>Aircraft day board</h2>
      <ul class="assets">
        {#each schedule as ac}
          <li>
            <div class="asset-head">
              <strong>{ac.tail}</strong>
              <span>{ac.status} · {ac.config}</span>
            </div>
            {#if ac.commitments?.length}
              <ul>
                {#each ac.commitments as c}
                  <li>
                    {c.role}: {c.callsign || c.mission}
                    {c.takeoff?.slice(11, 16)}–{c.land?.slice(11, 16)}
                  </li>
                {/each}
              </ul>
            {:else}
              <p class="muted">No commitments</p>
            {/if}
          </li>
        {/each}
      </ul>
    </section>
  {/if}

  {#if changes.length}
    <section class="ink" aria-label="Pen and ink log">
      <h2>Pen-and-ink</h2>
      <ul>
        {#each changes as ch}
          <li>
            <span class="when">{ch.at?.slice(11, 19)}</span>
            <span>L{ch.sortie_id} {ch.field}</span>
            <span class="muted">{ch.old_value || '—'} → {ch.new_value || '—'}</span>
          </li>
        {/each}
      </ul>
    </section>
  {/if}
</main>
