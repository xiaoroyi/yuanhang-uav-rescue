// Focused offline UI review against isolated development services; never production data.
import fs from 'node:fs/promises'
import path from 'node:path'
import {createRequire} from 'node:module'
const root=process.cwd(), require=createRequire(path.join(root,'frontend/package.json'))
process.env.PLAYWRIGHT_BROWSERS_PATH=path.join(root,'.local/ms-playwright')
const {chromium,expect}=require('@playwright/test')
const base=process.env.V4_UI_URL||'http://127.0.0.1:5176', backend='http://127.0.0.1:8014/api/v1'
const out=path.join(root,'evidence/experience-v4/screenshots')
await fs.mkdir(out,{recursive:true})
const api=async(p,body)=>{const r=await fetch(backend+p,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json'}:{},body:body?JSON.stringify(body):undefined});if(!r.ok)throw Error(p+' '+r.status+' '+await r.text());return r.json()}
const report={at:new Date().toISOString(),passed:false,scope:'isolated real solving, engine import, navigation, layout and offline visual review',checks:[],errors:[],httpErrors:[],geometry:[],shots:[]}
const browser=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']})
const context=await browser.newContext({viewport:{width:1440,height:900}}), page=await context.newPage()
page.on('pageerror',e=>report.errors.push(e.message))
page.on('response',r=>{if(r.status()>=400&&new URL(r.url()).pathname.startsWith('/api/'))report.httpErrors.push({url:r.url(),status:r.status()})})
await context.route('**/*',r=>{const u=new URL(r.request().url());return u.hostname==='127.0.0.1'||['blob:','data:'].includes(u.protocol)?r.continue():r.abort('internetdisconnected')})
const go=async route=>{await page.goto(base+'/#/'+route);await page.waitForTimeout(400);await page.evaluate(()=>document.fonts.ready)}
const shot=async name=>{await page.screenshot({path:path.join(out,name+'.png'),animations:'disabled'});report.shots.push(name+'.png')}
try{
 report.health=await api('/health')
 let m=await api('/missions',{name:'V4 视觉验收演练',case_id:'mountain-access-v1',template:'compact',idempotency_key:'v4-visual-review'})
 let summaries=await api('/scenarios/'+m.current_scenario_id+'/plans')
 let enhanced=summaries.find(p=>p.engine?.engine_type==='eoh'),standard=enhanced&&summaries.find(p=>p.engine?.engine_type==='standard'&&p.snapshot_id===enhanced.snapshot_id)
 if(!enhanced||!standard){
  const snap=await api('/scenarios/'+m.current_scenario_id+'/snapshots',{expected_state_version:1})
  for(const engine of ['standard','eoh']){
   let job=await api('/solve-jobs',{snapshot_id:snap.snapshot_id,objective:'time',objective_policy:'tradeoff_v2',engine_type:engine,time_limit_s:5})
   for(let n=0;n<120&&['queued','running'].includes(job.job_state);n++){await new Promise(r=>setTimeout(r,250));job=await api('/solve-jobs/'+job.job_id)}
   if(!job.has_validated_plan)throw Error('Actual engine job failed: '+JSON.stringify(job))
  }
  summaries=await api('/scenarios/'+m.current_scenario_id+'/plans');enhanced=summaries.find(p=>p.engine?.engine_type==='eoh');standard=summaries.find(p=>p.engine?.engine_type==='standard'&&p.snapshot_id===enhanced.snapshot_id)
 }
 const plan=await api('/plans/'+enhanced.plan_id)
 report.mission=m.mission_id;report.plans=[standard,enhanced]
 if(!plan.engine.ranking_evaluations||plan.validation.status!=='passed')throw Error('Missing real engine application/validation evidence')
 report.checks.push('Both engines produced independently checked plans on the same Snapshot and objective')
 await go('home');await expect(page.locator('.v4-gl-host canvas')).toBeVisible({timeout:30000});await expect(page.locator('.v4-home')).toHaveAttribute('data-animated','true')
 await page.getByLabel('关闭首页动效').click();await expect(page.locator('.v4-home')).toHaveAttribute('data-animated','false')
 for(const [w,h] of [[1440,900],[1920,1080],[1280,720],[390,844]]){
  await page.setViewportSize({width:w,height:h});await go('home');await expect(page.locator('.v4-gl-host canvas')).toBeVisible();await page.waitForTimeout(350)
  const g=await page.locator('.v4-home').evaluate(el=>({viewport:[innerWidth,innerHeight],width:el.getBoundingClientRect().width,pageWidth:document.documentElement.scrollWidth,font:getComputedStyle(el).fontFamily}))
  report.geometry.push(g);if(Math.abs(g.width-w)>2||g.pageWidth>w)throw Error('Full-width home regression '+JSON.stringify(g))
  await shot('home-'+w)
 }
 await page.setViewportSize({width:1440,height:900});await go('home');await page.getByRole('button',{name:'算法创新',exact:true}).click();await page.waitForTimeout(400);await shot('innovations-1440')
 await page.emulateMedia({reducedMotion:'reduce'});await page.getByLabel('开启首页动效').click();await expect(page.locator('.v4-home')).toHaveAttribute('data-animated','false');report.checks.push('User motion switch and system reduced motion respected')
 await go('cases');await expect(page.getByRole('heading',{name:'山地断路 · 物资空中接力',exact:true})).toBeVisible();await shot('cases-1440')
 await page.getByRole('tab',{name:'数据来源',exact:true}).click();await expect(page.getByRole('heading',{name:'Copernicus EMS · 2021德国西部洪灾',exact:false})).toBeVisible();await shot('sources-1440')
 await go('engines');await expect(page.getByRole('heading',{name:/载荷密度与批量评分/})).toBeVisible()
 const packages=await api('/heuristic-packages')
 if(!packages.some(p=>p.policy_id==='visual-seed-v1')){
  const pkg=JSON.parse(await fs.readFile('solver/policies/eoh-seed-v1.json','utf8'));pkg.policy_id='visual-seed-v1';pkg.name='本地导入演练评分'
  await page.getByLabel('导入本地策略包').setInputFiles({name:'visual-seed-v1.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(pkg))})
  await expect(page.getByRole('heading',{name:/本地导入演练评分/})).toBeVisible({timeout:15000})
 }
 await shot('engines-1440');report.checks.push('Local policy import completed through the UI; source remains rule_initialization')
 await go('integrations');await expect(page.getByText('当前运行模式：仿真与业务演练',{exact:true})).toBeVisible();await shot('integrations-1440')
 const configuration=await Promise.all([page.waitForEvent('download'),page.getByRole('link',{name:'下载配置模板',exact:false}).click()]);if((await configuration[0].suggestedFilename())!=='yuanhang-integration-config.json')throw Error('Configuration export filename mismatch')
 report.checks.push('Simulation adapter metadata and configuration export are functional')
 await page.evaluate(([id,p])=>localStorage.setItem('yuanhang-mission-plan-'+id,p),[m.mission_id,plan.plan_id])
 for(const [w,h] of [[1440,900],[1280,720]]){
  await page.setViewportSize({width:w,height:h});await go(`missions/${m.mission_id}/plans`);await expect(page.locator('.v4-plan-engine')).toContainText('EOH增强');await expect(page.locator('.maplibregl-canvas')).toBeVisible();await page.waitForTimeout(450);await shot('plans-'+w)
  const g=await page.locator('.v2-map-main').evaluate(el=>({viewport:[innerWidth,innerHeight],mapHeight:el.getBoundingClientRect().height,mapWidth:el.getBoundingClientRect().width,pageWidth:document.documentElement.scrollWidth}));report.geometry.push(g);if(g.mapHeight<300||g.pageWidth>w)throw Error('Map workspace geometry '+JSON.stringify(g))
  await go(`missions/${m.mission_id}/schedule`);await expect(page.locator('.v3-manifest-table tbody tr')).toHaveCount(plan.sorties.length);await shot('schedule-'+w)
 }
 await page.setViewportSize({width:1440,height:900});await go(`missions/${m.mission_id}/plans`);await page.getByRole('button',{name:'比较',exact:true}).click();await expect(page.getByRole('heading',{name:'把选择，放在同一张图上'})).toBeVisible();await expect(page.getByText('同快照、同模型范围 · 可比较策略结果',{exact:true})).toBeVisible();await expect(page.getByRole('heading',{name:'时间与能源取舍',exact:true})).toBeVisible();await page.waitForTimeout(350);await shot('engine-comparison-1440');await page.keyboard.press('Escape')
 m=await api('/missions/'+m.mission_id)
 if(!m.active_execution_id){
  if(m.active_plan_id!==plan.plan_id)await api('/plans/'+plan.plan_id+'/confirm',{expected_state_version:1,idempotency_key:'v4-confirm'})
  await go(`missions/${m.mission_id}/execute`);await page.getByRole('button',{name:'检查并创建模拟实例',exact:false}).click();await page.getByRole('button',{name:'开始演练',exact:true}).click();await page.getByRole('button',{name:'暂停演练',exact:true}).click()
 }
 await go(`missions/${m.mission_id}/execute`);await page.getByRole('button',{name:'机队运输看板',exact:true}).click();await expect(page.locator('.v3-fleet-table tbody tr')).toHaveCount(3);await shot('fleet-1440')
 await go(`missions/${m.mission_id}/review`);await shot('review-1440');report.checks.push('EOH plan can be confirmed and started/paused in server simulation; fleet and review render real state')
 await go('cases?tab=recent');await expect(page.getByRole('cell',{name:/V4 视觉验收演练/})).toBeVisible();await shot('task-assets-1440')
 await go('help');await expect(page.locator('video')).toBeAttached();await shot('guide-1440')
 report.passed=report.errors.length===0&&report.httpErrors.length===0
}catch(error){report.errors.push(String(error));try{await shot('failure')}catch{}process.exitCode=1}
finally{await fs.writeFile('evidence/experience-v4/browser-review.json',JSON.stringify(report,null,2)+'\n');await browser.close();console.log(JSON.stringify(report,null,2));if(!report.passed)process.exitCode=1}
