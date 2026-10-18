// Include actual bundled dependency license notices in the local application.
import fs from 'node:fs/promises'
import path from 'node:path'
import {fileURLToPath} from 'node:url'
const frontend=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..')
const pkg=JSON.parse(await fs.readFile(path.join(frontend,'package.json'),'utf8'))
const queue=Object.keys(pkg.dependencies),seen=new Set(),sections=[]
while(queue.length){
 const name=queue.shift();if(seen.has(name))continue;seen.add(name)
 const folder=path.join(frontend,'node_modules',name)
 let meta;try{meta=JSON.parse(await fs.readFile(path.join(folder,'package.json'),'utf8'))}catch{continue}
 queue.push(...Object.keys(meta.dependencies||{}))
 const names=await fs.readdir(folder)
 const licenses=names.filter(n=>/^(licen[sc]e|copying|notice)(\.|$)/i.test(n))
 const bodies=[];for(const file of licenses){const target=path.join(folder,file);if((await fs.stat(target)).isFile())bodies.push(`[${file}]\n`+await fs.readFile(target,'utf8'))}
 sections.push(`${name} ${meta.version}\nLicense: ${typeof meta.license==='string'?meta.license:JSON.stringify(meta.license||'See package source')}\n${meta.repository?.url||meta.homepage||''}\n\n${bodies.join('\n\n')||'Package does not include a root license text; see its published source.'}`)
}
await fs.writeFile(path.join(frontend,'public/THIRD_PARTY_NOTICES.txt'),'援航前端第三方组件声明\n\n以下为安装锁定版本的组件原文许可和声明。依赖内容依据各自许可分发；界面参考、原创素材及外部地图说明见 docs/experience-v3/RESEARCH.md。\n\n'+sections.sort().join('\n\n'+'='.repeat(72)+'\n\n')+'\n')
console.log(`Wrote ${sections.length} dependency notices.`)
