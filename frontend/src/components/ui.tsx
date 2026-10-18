import * as Dialog from '@radix-ui/react-dialog'
import { AlertCircle, CheckCircle2, LoaderCircle, X } from 'lucide-react'
import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { useContext } from 'react'
import clsx from 'clsx'
import { UIContext } from './UIContext'

export function Button({
  children,
  variant = 'default',
  busy = false,
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'default' | 'primary' | 'ghost' | 'danger'
  busy?: boolean
}) {
  return (
    <button
      className={clsx('button', `button-${variant}`, className)}
      {...props}
      disabled={props.disabled || busy}
    >
      {busy && <LoaderCircle size={15} className="spin" />}
      {children}
    </button>
  )
}
export function Badge({
  children,
  tone = 'neutral',
}: {
  children: ReactNode
  tone?: 'neutral' | 'teal' | 'amber' | 'red' | 'blue'
}) {
  return <span className={`badge badge-${tone}`}>{children}</span>
}
export function Modal({
  title,
  description,
  open,
  onOpenChange,
  children,
  wide = false,
}: {
  title: string
  description?: string
  open: boolean
  onOpenChange: (open: boolean) => void
  children: ReactNode
  wide?: boolean
}) {
  const context = useContext(UIContext)
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay" />
        <Dialog.Content
          className={clsx('dialog-content', wide && 'dialog-wide', context === 'v2' && 'v2-dialog')}
        >
          <div className="dialog-header">
            <div>
              <Dialog.Title className="dialog-title">{title}</Dialog.Title>
              <Dialog.Description className="dialog-description">
                {description || '修改将按当前场景版本保存，历史快照和方案保持可追溯。'}
              </Dialog.Description>
            </div>
            <Dialog.Close className="icon-button" aria-label="关闭弹窗">
              <X size={19} />
            </Dialog.Close>
          </div>
          {children}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
export function Empty({
  icon,
  title,
  description,
  action,
}: {
  icon: ReactNode
  title: string
  description: string
  action?: ReactNode
}) {
  return (
    <div className="empty">
      <div className="empty-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  )
}
export type ToastMessage = { id: number; message: string; tone: 'success' | 'error' | 'info' }
export function Toasts({
  messages,
  dismiss,
}: {
  messages: ToastMessage[]
  dismiss: (id: number) => void
}) {
  return (
    <div className="toasts" aria-live="polite">
      {messages.map((t) => (
        <div className={`toast toast-${t.tone}`} key={t.id}>
          {t.tone === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
          <span>{t.message}</span>
          <button onClick={() => dismiss(t.id)} aria-label="关闭通知">
            <X size={16} />
          </button>
        </div>
      ))}
    </div>
  )
}
