export interface TidalPoint {
  x: number
  y: number
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
