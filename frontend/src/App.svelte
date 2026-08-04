<script>
  import { onMount } from 'svelte'

  let sorties = $state([])
  let aircraft = $state([])
  let aircrew = $state([])
  let error = $state('')

  const api = (path, opts) => fetch('/api' + path, opts).then(r => {
    if (!r.ok) return r.json().then(e => Promise.reject(e.detail || r.statusText))
    return r.json()
  })

  async function load() {
    error = ''
    try {
      ;[sorties, aircraft, aircrew] = await Promise.all([
        api('/sorties'), api('/aircraft'), api('/aircrew')
      ])
    } catch (e) { error = String(e) }
  }

  async function setTail(sid, tail) {
    if (!tail) return
    try {
      await api(`/sorties/${sid}/aircraft`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tail })
      })
      await load()
    } catch (e) { error = String(e) }
  }

  async function setLoadout(sid, template) {
    if (!template) return
    try {
      await api(`/sorties/${sid}/loadout`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ template })
      })
      await load()
    } catch (e) { error = String(e) }
  }

  async function setCrew(sid, position, aircrew_id) {
    if (!aircrew_id) return
    try {
      await api(`/sorties/${sid}/crew`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ position, aircrew_id: +aircrew_id })
      })
      await load()
    } catch (e) { error = String(e) }
  }

  function crewName(s, pos) {
    return s.crew?.find(c => c.position === pos)?.name || '—'
  }

  onMount(load)
</script>

<main>
  <header>
    <h1>Squadron Schedule</h1>
    <button onclick={load}>Refresh</button>
  </header>

  {#if error}
    <p class="err">{error}</p>
  {/if}

  <table>
    <thead>
      <tr>
        <th>Takeoff</th>
        <th>Mission</th>
        <th>Tail</th>
        <th>Loadout</th>
        <th>Pilot</th>
        <th>WSO</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {#each sorties as s}
        <tr>
          <td>{s.takeoff?.slice(11, 16) || '—'}</td>
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
            <select value="" onchange={e => setLoadout(s.id, e.target.value)}>
              <option value="">{s.loadout ? s.loadout.slice(0, 18) + '…' : 'set…'}</option>
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
          <td>{s.status}</td>
        </tr>
      {/each}
    </tbody>
  </table>
</main>
