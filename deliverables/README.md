# 本机演示材料

双击仓库根目录demo.cmd，或直接打开yuanhang-demo.html。左右方向键、PageUp/PageDown翻页，Home/End跳到首尾。F11可使用浏览器全屏。HTML为单文件，截图已内嵌，不访问外部网络。yuanhang-demo.pdf可离线阅读或打印，共13页。

材料根据真实截图和已保存的求解JSON生成，源文件hash在evidence/demo/manifest.json。不把不同输入/不同模型的结果当作同条件算法优劣对比。第12页从最近完整验证记录读取计数，源码不匹配时明确标记仍待复验。

开发者重建：先完成scripts/verify.py --browser，再执行：

```powershell
node scripts/build-demo.mjs --require-verified
.venv\Scripts\python scripts/render_demo_qa.py
```

--require-verified会拒绝未与最新完整检查一致的源码。生成后需逐页检查实际PDF渲染，不能只看页面数或文本存在。

当前提供HTML/PDF演示稿，不是赛事官方提交模板。PPTX尚未导出：当前环境未提供Presentations技能要求的官方artifact-tool运行时，不能按该技能流程生成可编辑PPTX。未据此声称比赛材料或匿名审查全部完成。通用文案、截图与来源可供后续按官方模板整理。
