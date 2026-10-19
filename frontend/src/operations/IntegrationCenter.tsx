import { useQuery } from '@tanstack/react-query'
import {
  Activity,
  ArrowRight,
  Braces,
  CheckCircle2,
  Cpu,
  Download,
  FileJson2,
  HardDrive,
  Link2,
  Radio,
  RadioTower,
  Send,
  ShieldCheck,
} from 'lucide-react'
import type { components } from '../api/generated/http'
import { request } from '../api/client'

export function IntegrationCenter() {
  const integration = useQuery({
    queryKey: ['integration-overview'],
    queryFn: () => request<components['schemas']['IntegrationOverview']>('/integrations'),
  })
  return (
    <main className="v4-section-page">
      <header className="v4-page-head">
        <div>
          <span>
            <Link2 size={15} />
            设备、协议与API
          </span>
          <h1>统一适配，清晰交接。</h1>
          <p>
            任务编译、遥测回传与指令状态共享同一条可追溯链路。当前工作空间采用服务器业务仿真，设备适配合同支持按部署环境扩展。
          </p>
        </div>
        <a className="button" href="/api/v1/integrations/configuration" download>
          <Download size={15} />
          下载配置模板
        </a>
      </header>
      <section className="v4-integration-status">
        <div>
          <HardDrive size={30} />
          <p>
            <b>
              {integration.isError
                ? '服务连接中断，请恢复本机服务'
                : '当前运行模式：仿真与业务演练'}
            </b>
            <small>
              {integration.data
                ? '已安装 SimulationAdapter · 遥测来自服务器执行账本 · 真实设备连接：关闭'
                : '正在读取本机适配器状态…'}
            </small>
          </p>
        </div>
        <a href="#/missions" className="button primary">
          打开任务演练
          <ArrowRight size={14} />
        </a>
      </section>
      <div className="v4-adapter-flow">
        {[
          { icon: ShieldCheck, title: '计划验算', text: '只接收独立检查通过、版本匹配的方案。' },
          { icon: Braces, title: '任务编译', text: 'DeviceAdapter编译与校验任务格式。' },
          { icon: Send, title: '指令下发', text: '幂等、有效期、权限与执行版本共同约束。' },
          { icon: Radio, title: '遥测与回读', text: '分开记录上传、激活和设备观测状态。' },
          { icon: Activity, title: '状态核对', text: '受理、ACK、动作完成分别判断。' },
        ].map((s) => (
          <div key={s.title}>
            <s.icon size={24} />
            <b>{s.title}</b>
            <p>{s.text}</p>
          </div>
        ))}
      </div>
      <div className="v4-library-grid">
        {integration.data?.endpoints.map((e) => (
          <article key={e.path} className="v4-source-card">
            <h2>
              <RadioTower size={17} />
              {e.name}
            </h2>
            <div className="v4-endpoint">
              {e.method} {e.path}
            </div>
            <p>{e.description}</p>
          </article>
        ))}
      </div>
      <section className="v4-policy-card" style={{ marginTop: 24 }}>
        <h3>
          <FileJson2 size={18} /> 协议与部署资料
        </h3>
        <p>
          实际HTTP接口由服务自动生成；适配器实现继承后端DeviceAdapter。接入真实飞控时需配置服务端身份、传输和现场许可，页面不直接建立设备连接。
        </p>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginTop: 20 }}>
          <a className="button" href="/docs" target="_blank" rel="noreferrer">
            接口浏览器
            <ArrowRight size={14} />
          </a>
          <a className="button" href="/openapi.json" download>
            <Download size={14} />
            下载OpenAPI
          </a>
          <a className="button" href="#/engines">
            <Cpu size={14} />
            离线算法引擎
          </a>
        </div>
      </section>
      <p className="v4-engine-note">
        <CheckCircle2 size={14} />
        本机服务响应202表示已受理；设备ACK表示收到指令。只有后续状态回读与执行事实才能确认动作完成。
      </p>
    </main>
  )
}
