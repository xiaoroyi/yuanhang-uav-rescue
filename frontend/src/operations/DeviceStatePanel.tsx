import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { ops, type Execution, type Command } from '../api/operations'
import { Button } from '../components/ui'

const statusLabels: Record<Command['status'], string> = {
  queued: '请求已受理，等待发送',
  sent: '已发送，等待设备确认',
  acknowledged: '设备已确认，等待状态读回',
  succeeded: '完成，已取得独立状态读回',
  rejected: '设备拒绝',
  expired: '发送前已过期',
  indeterminate: '结果未确定，请独立核对状态',
}

export function DeviceStatePanel({ execution, device }: { execution: Execution; device: string }) {
  const cache = useQueryClient()
  const [receipt, setReceipt] = useState<Command | null>(null)
  const [pending, setPending] = useState(false)
  const [failure, setFailure] = useState('')
  const state = useQuery({
    queryKey: ['device-state', execution.execution_id, device],
    queryFn: () => ops.deviceState(execution.execution_id, device),
    enabled: execution.connected,
    refetchInterval: execution.connected ? 2000 : false,
    retry: false,
  })
  const command = useQuery({
    queryKey: ['device-command', receipt?.command_id],
    queryFn: () => ops.command(receipt!.command_id),
    enabled: !!receipt,
    refetchInterval: (query) =>
      ['queued', 'sent', 'acknowledged'].includes(query.state.data?.status || '') ? 400 : false,
  })
  const result = command.data || receipt
  const observed = state.data
  async function query() {
    setPending(true)
    setFailure('')
    try {
      setReceipt(await ops.queryDevice(execution, device))
      void cache.invalidateQueries({ queryKey: ['device-state', execution.execution_id, device] })
    } catch (error) {
      setFailure((error as Error).message)
    } finally {
      setPending(false)
    }
  }
  return (
    <section className="v2-device-state" aria-label="模拟设备程序核对">
      <h3>未来程序核对</h3>
      {!execution.connected && (
        <p role="status">模拟链路已断开；下列为最近记录，无法确认当前状态。</p>
      )}
      {state.isError && execution.connected && (
        <p role="alert">状态读回失败：{state.error.message}</p>
      )}
      {observed ? (
        <dl>
          <dt>已启用的未来程序</dt>
          <dd>
            <code>{observed.active_plan_id}</code>
          </dd>
          <dt>最近上传程序</dt>
          <dd>
            <code>{observed.uploaded_plan_id || '尚未上传替换程序'}</code>
          </dd>
          {observed.uploaded_content_sha256 && (
            <>
              <dt>已核对内容 SHA256</dt>
              <dd>
                <code title={observed.uploaded_content_sha256}>
                  {observed.uploaded_content_sha256.slice(0, 16)}…
                </code>
              </dd>
            </>
          )}
          <dt>设备状态版本 / 读回时间</dt>
          <dd>
            {observed.revision} ·{' '}
            {new Date(observed.observed_at).toLocaleTimeString('zh-CN', { hour12: false })}
          </dd>
        </dl>
      ) : state.isPending && execution.connected ? (
        <p>正在读取模拟设备状态…</p>
      ) : null}
      <Button
        disabled={
          !execution.connected ||
          pending ||
          ['queued', 'sent', 'acknowledged'].includes(result?.status || '')
        }
        busy={pending}
        onClick={() => void query()}
      >
        独立核对设备状态
      </Button>
      {result && (
        <p role="status" className="v2-command-receipt">
          <b>{statusLabels[result.status]}</b>
          <small>查询回执 {result.command_id}</small>
          {result.observed_state && (
            <small>
              已读回版本 {result.observed_state.revision} · {result.observed_state.device_id}
            </small>
          )}
        </p>
      )}
      {failure && <p role="alert">{failure}</p>}
      <p className="v2-subtle">在飞架次继续履行原承诺；未来程序的启用不代表已改写当前航段。</p>
    </section>
  )
}
