import { test, expect } from '@playwright/test'
import { fileURLToPath } from 'node:url'
import { formatChartValue } from '../src/pages/visual-analysis-data'

test('analysis axis tooltip keeps missing DEM unknown beside a valid cruise series', async ({
  page,
}, testInfo) => {
  // Exercise real ECharts, because the null data row is emitted only when another
  // series has a valid height at the same distance. A helper-only test misses that.
  await page.setContent('<div id="chart" style="width:600px;height:400px"></div>')
  await page.addScriptTag({
    path: fileURLToPath(new URL('../node_modules/echarts/dist/echarts.js', import.meta.url)),
  })
  const result = await page.evaluate(async (formatterSource) => {
    // This is the serialized source helper from this checkout, not user content.
    const format = new Function(`return (${formatterSource})`)() as typeof formatChartValue
    const library = (window as unknown as { echarts: typeof import('echarts') }).echarts
    const host = document.getElementById('chart')!
    const chart = library.init(host)
    const seen: unknown[] = []
    const ground = [
      [0, null],
      [1, 0],
      [2, 30],
    ]
    chart.setOption({
      animation: false,
      tooltip: {
        trigger: 'axis',
        valueFormatter: (value: unknown) => {
          seen.push(value)
          return format(value, 2, ' m')
        },
      },
      xAxis: { type: 'value' },
      yAxis: { type: 'value' },
      series: [
        { type: 'line', name: 'DEM地面采样', data: ground },
        {
          type: 'line',
          name: '模型巡航高程',
          data: [
            [0, 100],
            [1, 100],
            [2, 100],
          ],
        },
      ],
    })
    const readTip = async (dataIndex: number) => {
      chart.dispatchAction({ type: 'showTip', seriesIndex: 1, dataIndex })
      await new Promise((resolve) => setTimeout(resolve, 80))
      return document.body.innerText
    }
    try {
      return { missing: await readTip(0), zero: await readTip(1), seen, ground }
    } finally {
      chart.dispose()
    }
  }, formatChartValue.toString())
  expect(result.seen).toContain(null)
  expect(result.missing).toContain('未知')
  expect(result.missing).toContain('100 m')
  expect(result.missing.split('\n')).not.toContain('0 m')
  expect(result.zero.split('\n')).toContain('0 m')
  expect(result.ground[0][1]).toBeNull()
  await testInfo.attach('analysis-unknown-versus-zero-tooltip', {
    body: JSON.stringify(result, null, 2),
    contentType: 'application/json',
  })
})
