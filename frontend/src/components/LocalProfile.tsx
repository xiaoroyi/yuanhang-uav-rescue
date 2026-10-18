import { useEffect, useState, type FormEvent } from 'react'
import { Check, Laptop, ShieldCheck, UserRound } from 'lucide-react'
import { Button, Modal } from './ui'
import './local-profile.css'

export type LocalProfile = {
  displayName: string
  team: string
  role: string
  color: string
}

export const LOCAL_PROFILE_COLORS = [
  { value: '#6366f1', label: '星河靛蓝' },
  { value: '#0891b2', label: '深海青蓝' },
  { value: '#9333ea', label: '极光紫' },
  { value: '#d97706', label: '曙光琥珀' },
  { value: '#e11d48', label: '珊瑚玫红' },
] as const

const STORAGE_KEY = 'yuanhang.local-profile.v1'
const CHANGE_EVENT = 'yuanhang:local-profile-change'
const DEFAULT_PROFILE: LocalProfile = {
  displayName: '本机调度员',
  team: '援航救援工作组',
  role: '调度负责人',
  color: LOCAL_PROFILE_COLORS[0].value,
}

function cleanText(value: unknown, max: number, fallback: string) {
  if (typeof value !== 'string') return fallback
  const cleaned = value
    .normalize('NFC')
    .replace(/\p{Cc}/gu, ' ')
    .replace(/\p{Cf}/gu, '')
    .replace(/\s+/gu, ' ')
    .trim()
  return Array.from(cleaned).slice(0, max).join('') || fallback
}

export function sanitizeLocalProfile(value: unknown): LocalProfile {
  const input = value && typeof value === 'object' ? (value as Record<string, unknown>) : {}
  return {
    displayName: cleanText(input.displayName, 24, DEFAULT_PROFILE.displayName),
    team: cleanText(input.team, 40, DEFAULT_PROFILE.team),
    role: cleanText(input.role, 24, DEFAULT_PROFILE.role),
    color: LOCAL_PROFILE_COLORS.some((c) => c.value === input.color)
      ? (input.color as string)
      : DEFAULT_PROFILE.color,
  }
}

function readLocalProfile(): LocalProfile {
  try {
    return sanitizeLocalProfile(JSON.parse(window.localStorage.getItem(STORAGE_KEY) || 'null'))
  } catch {
    return { ...DEFAULT_PROFILE }
  }
}

export function useLocalProfile() {
  const [profile, setProfile] = useState<LocalProfile>(readLocalProfile)
  const [persistenceAvailable, setPersistenceAvailable] = useState(true)

  useEffect(() => {
    const refresh = () => setProfile(readLocalProfile())
    const onStorage = (event: StorageEvent) => {
      if (event.key === STORAGE_KEY || event.key === null) refresh()
    }
    window.addEventListener(CHANGE_EVENT, refresh)
    window.addEventListener('storage', onStorage)
    return () => {
      window.removeEventListener(CHANGE_EVENT, refresh)
      window.removeEventListener('storage', onStorage)
    }
  }, [])

  function saveProfile(value: LocalProfile) {
    const next = sanitizeLocalProfile(value)
    setProfile(next)
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
      setPersistenceAvailable(true)
      window.dispatchEvent(new Event(CHANGE_EVENT))
    } catch {
      setPersistenceAvailable(false)
    }
  }

  function resetProfile() {
    saveProfile({ ...DEFAULT_PROFILE })
  }

  return { profile, saveProfile, resetProfile, persistenceAvailable }
}

function ProfileForm({
  profile,
  onSave,
  onClose,
}: {
  profile: LocalProfile
  onSave: (profile: LocalProfile) => void
  onClose: () => void
}) {
  const [draft, setDraft] = useState(profile)
  const [error, setError] = useState('')
  const initials = Array.from(draft.displayName.trim() || '援')
    .slice(0, 1)
    .join('')
  function submit(event: FormEvent) {
    event.preventDefault()
    if (!draft.displayName.trim() || !draft.team.trim() || !draft.role.trim()) {
      setError('请填写显示名称、团队和职责。')
      return
    }
    onSave(sanitizeLocalProfile(draft))
    onClose()
  }
  return (
    <form onSubmit={submit} className="local-profile-form">
      <div className="local-profile-preview">
        <span
          className="local-profile-avatar"
          style={{ background: draft.color }}
          aria-hidden="true"
        >
          {initials}
        </span>
        <div>
          <span className="local-profile-eyebrow">YOUR MISSION IDENTITY</span>
          <strong>{draft.displayName.trim() || '设置你的显示名称'}</strong>
          <span>
            {draft.team.trim() || '你的团队'} · {draft.role.trim() || '你的职责'}
          </span>
        </div>
        <span className="local-profile-device">
          <Laptop size={13} /> 本机
        </span>
      </div>
      <div className="local-profile-fields">
        <label className="field">
          <span>
            显示名称 <small>最多24字</small>
          </span>
          <input
            name="displayName"
            autoComplete="nickname"
            maxLength={24}
            value={draft.displayName}
            onChange={(event) => setDraft({ ...draft, displayName: event.target.value })}
            placeholder="如：小罗"
            required
          />
        </label>
        <label className="field">
          <span>
            团队 <small>最多40字</small>
          </span>
          <input
            name="team"
            autoComplete="organization"
            maxLength={40}
            value={draft.team}
            onChange={(event) => setDraft({ ...draft, team: event.target.value })}
            placeholder="如：援航项目组"
            required
          />
        </label>
        <label className="field">
          <span>
            当前职责 <small>最多24字</small>
          </span>
          <input
            name="role"
            maxLength={24}
            value={draft.role}
            onChange={(event) => setDraft({ ...draft, role: event.target.value })}
            placeholder="如：算法与调度 / 系统开发"
            required
          />
        </label>
        <fieldset className="local-profile-colors">
          <legend>头像色彩</legend>
          <div>
            {LOCAL_PROFILE_COLORS.map((color) => (
              <button
                type="button"
                key={color.value}
                aria-label={color.label}
                aria-pressed={draft.color === color.value}
                title={color.label}
                style={{ background: color.value }}
                onClick={() => setDraft({ ...draft, color: color.value })}
              >
                {draft.color === color.value && <Check size={17} />}
              </button>
            ))}
          </div>
        </fieldset>
      </div>
      <div className="local-profile-privacy">
        <ShieldCheck size={19} />
        <p>
          <strong>保存在这个浏览器的本机档案</strong>
          用于显示姓名和团队，无需注册。它不创建服务器账户，也不提供登录、权限或审核签名；清理浏览器数据会重置档案。
        </p>
      </div>
      {error && (
        <p className="local-profile-error" role="alert">
          {error}
        </p>
      )}
      <div className="dialog-footer local-profile-footer">
        <span>
          <UserRound size={14} /> 不影响场景、方案和历史记录
        </span>
        <Button type="submit" variant="primary">
          保存档案
        </Button>
      </div>
    </form>
  )
}

export function LocalProfileDialog({
  open,
  onOpenChange,
  profile,
  onSave,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  profile: LocalProfile
  onSave: (profile: LocalProfile) => void
}) {
  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title="我的本机档案"
      description="为这台设备设置显示身份。所有规划数据仍保存在本机服务，档案不构成权限认证。"
    >
      <ProfileForm
        key={`${open}-${profile.displayName}-${profile.team}-${profile.role}-${profile.color}`}
        profile={profile}
        onSave={onSave}
        onClose={() => onOpenChange(false)}
      />
    </Modal>
  )
}
