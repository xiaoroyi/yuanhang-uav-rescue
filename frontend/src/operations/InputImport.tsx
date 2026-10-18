import { useRef, useState } from 'react'
import { Download, Upload } from 'lucide-react'
import type { components } from '../api/generated/http'
import { ApiError } from '../api/client'
import type { Mission, MissionDraft } from '../api/operations'
import { Button, Modal } from '../components/ui'

export function InputImport({
  mission,
  group,
  onSave,
  notify,
}: {
  mission: Mission
  group: 'sites' | 'demands' | 'cargo_items' | 'drones' | 'batteries' | 'drone_types'
  onSave: (draft: MissionDraft) => Promise<void>
  notify: (m: string, error?: boolean) => void
}) {
  const file = useRef<HTMLInputElement>(null)
  const [entity, setEntity] = useState(group)
  const [busy, setBusy] = useState(false)
  const [preview, setPreview] = useState<components['schemas']['DraftImportPreview'] | null>(null)
  async function load(input: File) {
    setBusy(true)
    try {
      const data = new FormData()
      data.append('file', input)
      const response = await fetch(
        `/api/v1/missions/${mission.mission_id}/input-preview?entity=${entity}`,
        { method: 'POST', body: data },
      )
      const value = await response.json()
      if (!response.ok) throw new ApiError(response.status, value)
      setPreview(value as components['schemas']['DraftImportPreview'])
    } catch (e) {
      notify((e as Error).message, true)
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="v2-input-import">
      <select
        aria-label="导入实体表"
        value={entity}
        onChange={(e) => setEntity(e.target.value as typeof entity)}
      >
        {Object.entries({
          sites: '需求点',
          demands: '救援需求',
          cargo_items: '箱件库存',
          drones: '机体',
          batteries: '电池',
          drone_types: '机型',
        }).map(([id, name]) => (
          <option value={id} key={id}>
            {name}
          </option>
        ))}
      </select>
      <input
        type="file"
        ref={file}
        accept=".csv,.xlsx,.json"
        hidden
        onChange={(e) => {
          const f = e.target.files?.[0]
          if (f) void load(f)
          e.target.value = ''
        }}
      />
      <Button busy={busy} onClick={() => file.current?.click()}>
        <Upload size={14} />
        导入数据
      </Button>
      <a
        className="button"
        href={`/api/v1/missions/${mission.mission_id}/input-template?entity=${entity}&format=csv`}
      >
        <Download size={14} />
        当前 CSV 模板
      </a>
      <a
        className="button"
        href={`/api/v1/missions/${mission.mission_id}/input-template?format=xlsx`}
      >
        <Download size={14} />
        完整 Excel 模板
      </a>
      <Modal
        title="任务输入导入预览"
        description="确认后更新本任务输入；不会创建无关场景，也不会改写历史方案。"
        open={!!preview}
        onOpenChange={(v) => {
          if (!v) setPreview(null)
        }}
      >
        {preview && (
          <div className="v2-repair-preview">
            <p>
              需求点 {preview.draft.sites?.length || 0} · 需求 {preview.draft.demands?.length || 0}{' '}
              · 库存 {preview.draft.cargo_items?.length || 0} · 机体{' '}
              {preview.draft.drones?.length || 0} · 电池 {preview.draft.batteries?.length || 0}
            </p>
            {preview.notices.map((s) => (
              <p className="v2-subtle" key={s}>
                {s}
              </p>
            ))}
            <div className="v2-form-actions">
              <Button onClick={() => setPreview(null)}>返回修改</Button>
              <Button
                variant="primary"
                busy={busy}
                onClick={() => {
                  setBusy(true)
                  void onSave(preview.draft)
                    .then(() => {
                      setPreview(null)
                      notify('任务输入已保存，请重新运行条件检查。')
                    })
                    .catch((e: Error) => notify(e.message, true))
                    .finally(() => setBusy(false))
                }}
              >
                确认更新任务输入
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
