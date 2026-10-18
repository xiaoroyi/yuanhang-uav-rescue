// Runs against an explicitly isolated local V2 service, never the demonstration DB.
import fs from 'node:fs/promises'
import path from 'node:path'
import {createRequire} from 'node:module'
const root=process.cwd(), require=createRequire(path.join(root,'frontend/package.json'))
process.env.PLAYWRIGHT_BROWSERS_PATH=path.join(root,'.local/ms-playwright')
const {chromium,expect}=require('@playwright/test')
const base=process.env.YUANHANG_V2_QA_URL || 'http://127.0.0.1:8013'
if(!/^http:\/\/127\.0\.0\.1:(8013)$/.test(base))throw Error('V2 QA requires an isolated test port')
const out=path.join(root,'evidence/redesign-v2/screenshots');await fs.mkdir(out,{recursive:true})
const browser=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']})
const context=await browser.newContext({viewport:{width:1440,height:900},reducedMotion:'reduce'})
const errors=[],network=[],screenshots=[],geometry=[]
await context.route('**/*',r=>{const u=new URL(r.request().url());if(u.hostname==='127.0.0.1'||u.protocol==='blob:'||u.protocol==='data:')return r.continue();network.push(u.origin);return r.abort('internetdisconnected')})
const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message))
const shot=async name=>{await page.waitForTimeout(1200);await page.screenshot({path:path.join(out,name+'.png'),animations:'disabled'});screenshots.push(name+'.png')}
const api=async(p,body)=>{const r=await fetch(base+'/api/v1'+p,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json'}:{},body:body?JSON.stringify(body):undefined});if(!r.ok)throw Error(p+' '+r.status+' '+await r.text());return r.json()}
let mission,plan,execution
try{
 await page.goto(base)
 await expect(page.getByRole('heading',{name:'救援工作首页',exact:true})).toBeVisible()
 await page.getByRole('button',{name:'运行示例演练',exact:false}).click()
 await page.getByPlaceholder('例如：镇龙乡山洪应急运输').fill('V2 浏览器完整演练 '+Date.now())
 await shot('new-1440')
 await page.getByRole('button',{name:'创建并准备任务',exact:false}).click()
 await expect(page.locator('.v2-mission-heading h1')).toContainText('V2 浏览器完整演练')
 mission=page.url().match(/missions\/([^/]+)/)[1]
 await shot('prepare-1440')
 await page.getByRole('button',{name:'条件检查',exact:false}).click()
 await page.getByRole('button',{name:'运行检查',exact:true}).click()
 await expect(page.locator('.v2-check-summary')).toContainText('0 项待处理')
 await shot('checks-1440')
 await page.getByRole('button',{name:'进入方案计算',exact:false}).click()
 await page.getByRole('button',{name:'生成方案',exact:true}).click()
 await expect(page.locator('.v2-metrics-line')).toContainText('32 箱',{timeout:60000})
 await page.waitForTimeout(1500)
 plan=await page.getByLabel('选择调度方案').inputValue()
 for(const [w,h]of[[1440,900],[1280,720]]){
  await page.setViewportSize({width:w,height:h});await shot('plans-'+w)
  geometry.push(await page.locator('.v2-map-main').evaluate(e=>({viewport:[innerWidth,innerHeight],mapHeight:e.getBoundingClientRect().height,mapWidth:e.getBoundingClientRect().width,pageWidth:document.documentElement.scrollWidth})))
 }
 await page.setViewportSize({width:1440,height:900})
 await page.getByRole('button',{name:/^架次 \d+/}).click()
 await page.locator('.v2-object-scroll button').first().click()
 await expect(page.locator('.v2-inspector')).toContainText('运输电池')
 await page.getByRole('button',{name:'查看高程 / 载荷 / 电量',exact:true}).click()
 await shot('sortie-profile-1440')
 await page.getByRole('button',{name:'关闭详情',exact:true}).click()
 await page.getByRole('button',{name:'机体 / 电池排程',exact:true}).click()
 await shot('gantt-1440')
 await page.getByRole('button',{name:'确认方案',exact:true}).click()
 await expect(page.locator('.toast').last()).toContainText('方案已确认')
 await page.locator('.v2-stage-tabs').getByRole('link',{name:/执行跟踪/}).click()
 await page.getByRole('button',{name:'检查并创建模拟实例',exact:false}).click()
 await page.getByRole('button',{name:'开始演练',exact:true}).click()
 await expect(page.locator('.v2-plan-toolbar')).toContainText('运行中')
 await shot('execution-running-1440')
 await page.getByRole('button',{name:'暂停演练',exact:true}).click()
 const m=await api('/missions/'+mission);execution=m.active_execution_id
 const original=await api('/plans/'+plan)
 let e=await api('/executions/'+execution)
 const first=Math.min(...original.sorties.flatMap(r=>r.visits.map(v=>v.delivery_complete_s)))+1
 e=await api(`/executions/${execution}/simulation/actions`,{action:'advance',expected_revision:e.revision,idempotency_key:'qa-'+Date.now(),target_time_s:first})
 await page.reload();await expect(page.locator('.v2-metrics-line')).toContainText('模拟已交付')
 await shot('execution-paused-1440')
 await page.getByRole('button',{name:'上报变化',exact:true}).click()
 await page.getByLabel('变化类型').selectOption('demand.added')
 await page.getByLabel('变化原因').fill('浏览器验收：明确新增一箱医疗物资和实物库存')
 await page.getByRole('button',{name:'记录事件并分析影响',exact:true}).click()
 await expect(page.locator('.v2-event-list')).toContainText('浏览器验收')
 await page.getByRole('button',{name:'生成调整',exact:true}).click()
 await expect(page.locator('.v2-repair-preview')).toContainText('状态 ready',{timeout:60000})
 await shot('repair-diff-1440')
 await page.getByRole('button',{name:'确认采纳模拟调整',exact:true}).click()
 await expect(page.locator('.v2-repair-preview')).toContainText('状态 applied')
 await page.getByRole('button',{name:'关闭详情',exact:true}).click()
 await page.locator('.v2-stage-tabs').getByRole('link',{name:/复盘分析/}).click()
 await shot('review-1440')
 await page.setViewportSize({width:1280,height:720});await shot('review-1280')
 await page.goto(base+'/#/home');await shot('home-1280')
 await page.setViewportSize({width:1440,height:900});await shot('home-1440')
 const report={passed:errors.length===0&&geometry.every(g=>g.pageWidth<=g.viewport[0]&&g.mapHeight>=(g.viewport[0]===1440?440:340)),at:new Date().toISOString(),base,mission,plan,execution,errors,external_requests:network,screenshots,geometry}
 await fs.writeFile(path.join(out,'../browser-review.json'),JSON.stringify(report,null,2)+'\n')
 console.log(JSON.stringify(report,null,2));if(!report.passed)process.exitCode=1
}catch(e){await shot('failure');console.error(e);process.exitCode=1}finally{await browser.close()}
