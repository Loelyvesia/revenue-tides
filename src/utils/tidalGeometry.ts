export interface TidalPoint {
  x: number
  y: number
}

export interface TidalBodyOptions {
  baseDepth?: number
  peakContribution?: number
  slopeContribution?: number
  minDepth?: number
  maxDepth?: number
  tension?: number
}

function fixed(value: number): string {
  return Number.isFinite(value) ? value.toFixed(2) : '0'
}

/**
 * Catmull-Rom converted to cubic Beziers. The curve passes through every real
 * quarter anchor; points between anchors are presentational geometry only.
 */
export function smoothPath(points: TidalPoint[], tension = 0.82): string {
  if (!points.length) return ''
  if (points.length === 1) return `M${fixed(points[0].x)},${fixed(points[0].y)}`
  const scale = Math.max(0, Math.min(tension, 1)) / 6
  let path = `M${fixed(points[0].x)},${fixed(points[0].y)}`
  for (let index = 0; index < points.length - 1; index += 1) {
    const p0 = points[index - 1] ?? points[index]
    const p1 = points[index]
    const p2 = points[index + 1]
    const p3 = points[index + 2] ?? p2
    const c1x = p1.x + (p2.x - p0.x) * scale
    const c1y = p1.y + (p2.y - p0.y) * scale
    const c2x = p2.x - (p3.x - p1.x) * scale
    const c2y = p2.y - (p3.y - p1.y) * scale
    path += ` C${fixed(c1x)},${fixed(c1y)} ${fixed(c2x)},${fixed(c2y)} ${fixed(p2.x)},${fixed(p2.y)}`
  }
  return path
}

export function ribbonPath(points: TidalPoint[], halfWidth: number | ((point: TidalPoint, index: number) => number), tension = 0.82): string {
  if (!points.length) return ''
  const widthAt = (point: TidalPoint, index: number): number => typeof halfWidth === 'function' ? halfWidth(point, index) : halfWidth
  const upper = points.map((point, index) => ({ x: point.x, y: point.y - widthAt(point, index) }))
  const lower = points.map((point, index) => ({ x: point.x, y: point.y + widthAt(point, index) })).reverse()
  const upperPath = smoothPath(upper, tension)
  const lowerPath = smoothPath(lower, tension).replace(/^M/, 'L')
  return `${upperPath} ${lowerPath} Z`
}

export function areaToBaselinePath(points: TidalPoint[], baseline: number, tension = 0.82): string {
  if (!points.length) return ''
  return `${smoothPath(points, tension)} L${fixed(points.at(-1)!.x)},${fixed(baseline)} L${fixed(points[0].x)},${fixed(baseline)} Z`
}

/**
 * The canonical UI 2.3 surface primitive. Quarterly anchors form the upper
 * waterline while the lower edge softly follows a presentation-only depth.
 * The lower edge never encodes a second research variable.
 */
export function tidalAreaPath(
  points: TidalPoint[],
  baseline: number,
  depth: number | ((point: TidalPoint, index: number) => number) = 0,
  tension = 0.82,
): string {
  if (!points.length) return ''
  const depthAt = (point: TidalPoint, index: number): number => typeof depth === 'function' ? depth(point, index) : depth
  const floor = points.map((point, index) => ({
    x: point.x,
    y: Math.min(baseline, baseline - depthAt(point, index)),
  })).reverse()
  return `${smoothPath(points, tension)} ${smoothPath(floor, tension).replace(/^M/, 'L')} Z`
}

/**
 * A floating tidal body. The upper surface passes through every quarterly
 * anchor. The lower contour follows that surface with restrained, purely
 * presentational depth and must never be read as a second variable.
 */
export function tidalBodyPath(points: TidalPoint[], options: TidalBodyOptions = {}): string {
  if (!points.length) return ''
  const {
    baseDepth = 24,
    peakContribution = 8,
    slopeContribution = 0.1,
    minDepth = baseDepth * 0.78,
    maxDepth = baseDepth * 1.55,
    tension = 0.82,
  } = options
  const ys = points.map((point) => point.y)
  const low = Math.min(...ys)
  const high = Math.max(...ys)
  const span = Math.max(high - low, 1)
  const lower = points.map((point, index) => {
    const previous = points[index - 1] ?? point
    const next = points[index + 1] ?? point
    const peakRatio = (high - point.y) / span
    const localSlope = Math.abs(next.y - previous.y)
    const rawDepth = baseDepth + peakRatio * peakContribution + localSlope * slopeContribution
    const depth = Math.max(minDepth, Math.min(maxDepth, rawDepth))
    return { x: point.x, y: point.y + depth }
  }).reverse()
  return `${smoothPath(points, tension)} ${smoothPath(lower, tension).replace(/^M/, 'L')} Z`
}

/** A wider, softer mass beneath the canonical surface. */
export function tidalEnvelopePath(points: TidalPoint[], baseDepth = 30, spread = 10, tension = 0.82): string {
  if (!points.length) return ''
  const softened = points.map((point, index) => {
    const previous = points[index - 1] ?? point
    const next = points[index + 1] ?? point
    const slope = Math.min(Math.abs(next.y - previous.y), 42)
    return { x: point.x, y: point.y + spread * .22 + slope * 0.04 }
  })
  return tidalBodyPath(softened, {
    baseDepth: baseDepth + spread,
    peakContribution: spread * .55,
    slopeContribution: .08,
    minDepth: baseDepth * .82,
    maxDepth: (baseDepth + spread) * 1.45,
    tension,
  })
}

/**
 * Creates two non-stacked definition currents from one anchor sequence.
 * Separation is visual only and is intended for reporting-version overlap.
 */
export function tidalSplitPaths(points: TidalPoint[], offset = 12, depth = 14, tension = 0.82): { upper: string; lower: string } {
  const upper = points.map((point) => ({ x: point.x, y: point.y - offset }))
  const lower = points.map((point) => ({ x: point.x, y: point.y + offset }))
  return {
    upper: tidalBodyPath(upper, { baseDepth: depth, tension }),
    lower: tidalBodyPath(lower, { baseDepth: depth, tension }),
  }
}

/** Deterministic SVG stop list used by masks that dissolve a tide edge. */
export function tidalFadeMask(): ReadonlyArray<{ offset: string; opacity: number }> {
  return [
    { offset: '0%', opacity: 0 },
    { offset: '12%', opacity: 0.88 },
    { offset: '76%', opacity: 1 },
    { offset: '100%', opacity: 0 },
  ]
}
