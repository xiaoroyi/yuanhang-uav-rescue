/** A quad is shown only when all four original samples are valid. Never bridge NoData. */
export function terrainMeshIndices(elevations: (number | null)[][]): number[] {
  const height = elevations.length,
    width = elevations[0]?.length || 0
  const indices: number[] = []
  for (let y = 0; y < height - 1; y++)
    for (let x = 0; x < width - 1; x++) {
      if (
        elevations[y][x] == null ||
        elevations[y][x + 1] == null ||
        elevations[y + 1][x] == null ||
        elevations[y + 1][x + 1] == null
      )
        continue
      const a = y * width + x
      indices.push(a, a + width, a + 1, a + 1, a + width, a + width + 1)
    }
  return indices
}
