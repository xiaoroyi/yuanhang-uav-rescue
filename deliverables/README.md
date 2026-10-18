# 本机演示材料

双击仓库根目录demo.cmd，或直接打开yuanhang-demo.html。左右方向键、PageUp/PageDown翻页，Home/End跳到首尾。F11可使用浏览器全屏。HTML为单文件，截图已内嵌，不访问外部网络。yuanhang-demo.pdf可离线阅读或打印，共15页，最终PDF已经逐页视觉检查；页数与源码验收身份见evidence/demo/manifest.json及pdf-qa.json。

材料根据真实截图和已保存的求解JSON生成，源文件hash在evidence/demo/manifest.json。不把不同输入/不同模型的结果当作同条件算法优劣对比。第14页从最近完整验证记录读取计数，源码不匹配时明确标记仍待复验。

开发者重建：先完成scripts/verify.py --browser，再执行：

```powershell
node scripts/build-demo.mjs --require-verified
.venv\Scripts\python scripts/render_demo_qa.py
```

--require-verified会拒绝未与最新完整检查一致的源码。生成后需逐页检查实际PDF渲染，不能只看页面数或文本存在。

当前提供HTML/PDF演示稿，不是赛事官方提交模板。PPTX尚未导出：当前环境未提供Presentations技能要求的官方artifact-tool运行时，不能按该技能流程生成可编辑PPTX。未据此声称比赛材料或匿名审查全部完成。通用文案、截图与来源可供后续按官方模板整理。

## 实际操作录像

打开walkthrough.html播放yuanhang-walkthrough.webm，1440×900、70.52秒，含中文字幕和12个章节跳转。保留真实计算等待时间，无旁白；它是实际生产构建的浏览器操作，不是实飞或遥测。视频、播放器、封面、字幕需放在同一目录。walkthrough-analysis.json为录制中实际下载的分析文件。

复现命令为`node scripts/record-demo.mjs --require-verified`，然后`node scripts/check-demo-video.mjs`。前者要求已有当前生产构建和完整回归，使用独立8021端口与.local/video-runtime下的新数据库，保留该记录，不修改runtime演示库。后者实际解码视频、检查字幕与章节并截图供视觉核验。若8021已占用会停止，不关闭别人的服务。

录像的原始Snapshot、Plan、事件、源码hash和视频SHA在evidence/video/recording.json。最终视频已经实际解码，12段字幕及章节控件通过检查，6处章节跳转画面已分别查看，且无外网请求/页面异常，见evidence/video/playback-qa.json。录制和保存依据[Playwright官方视频说明](https://playwright.dev/docs/videos)，关闭Context后保存完整视频。
