// A repair snapshot contains remaining work, not the whole rescue mission.
// Keep the initial inventory and execution facts when displaying mission totals.
export function executionCargoProgress(
  initial: string[],
  current: string[],
  delivered: string[],
  loaded: string[],
  scheduled: string[] = [],
) {
  const doneSet = new Set(delivered),
    loadedSet = new Set(loaded.filter((id) => !doneSet.has(id)))
  const all = new Set([...initial, ...current, ...doneSet, ...loadedSet, ...scheduled])
  return {
    total: all.size,
    done: doneSet.size,
    loaded: loadedSet.size,
    pending: all.size - doneSet.size - loadedSet.size,
  }
}
