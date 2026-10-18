import { useEffect, useRef } from 'react'
import * as echarts from 'echarts'

export function DataChart({
  option,
  label,
  height = 280,
}: {
  option: echarts.EChartsOption
  label: string
  height?: number
}) {
  const node = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!node.current) return
    const chart = echarts.init(node.current)
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const paint = () => {
      const dark = document.documentElement.dataset.theme !== 'light'
      const color = dark ? '#a7b9d1' : '#526b86',
        line = dark ? '#8299b31c' : '#dce5ef'
      const axisTheme = (value: unknown) => {
        const list = Array.isArray(value) ? value : value ? [value] : []
        return list.map((item: Record<string, unknown>) => ({
          ...item,
          axisLabel: { ...((item.axisLabel as object) || {}), color },
          nameTextStyle: { ...((item.nameTextStyle as object) || {}), color },
          splitLine: { lineStyle: { color: line } },
          axisLine: { lineStyle: { color: dark ? '#344963' : '#c1cfdf' } },
        }))
      }
      chart.setOption({
        animation: !reduce,
        animationDuration: 550,
        ...option,
        xAxis: axisTheme(option.xAxis),
        yAxis: axisTheme(option.yAxis),
        legend: { bottom: 2, textStyle: { color } },
        tooltip: {
          trigger: 'axis',
          backgroundColor: dark ? '#15243a' : '#fff',
          borderColor: line,
          textStyle: { color: dark ? '#e2ecfa' : '#294059' },
          confine: true,
        },
      })
    }
    paint()
    const theme = new MutationObserver(paint)
    theme.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    const resize = new ResizeObserver(() => chart.resize())
    resize.observe(node.current)
    return () => {
      resize.disconnect()
      theme.disconnect()
      chart.dispose()
    }
  }, [option])
  return (
    <div ref={node} role="img" aria-label={label} style={{ height, minWidth: 0, width: '100%' }} />
  )
}
