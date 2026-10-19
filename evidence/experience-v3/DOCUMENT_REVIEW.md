# 当前项目文档交付检查

2026年10月19日，任务V3-12。按用户要求，以产品代码基线803c295重写实际项目总文档，不修改业务实现和原始开发方案。

## 内容依据

核对了桌面原开发Word与仓库原件的SHA256一致性、原题约束映射、当前solver物理/目标/构造/有限池/联合/天气/修复边界、前后端入口、操作DTO、实际OpenAPI、数据库与Worker，以及V3已有实跑案例和交接证据。重新说明原基础、新增实现、未完成研究与不能直接使用的宣传口径。没有重跑求解或全量业务回归，也未把旧测试计数当成本次验证。

主源为docs/PROJECT_DOSSIER.md，23章；包含模型公式、原方案差异、申报素材、最小必读/按模块索引与完整接手提示词。独立提示词由主文档第21章提取，逐字核对；Word由同一主文档生成，保留7个原生可编辑公式和17张内容表，另有目录表。

## 文档检查

- 实际OpenAPI的83个路径模板与核心路径对照；不是83个独立功能。
- 3个已有案例的箱件、架次、能源和耗时与原JSON核对；保留旧记录身份和检查范围。
- 原开发Word未改写，桌面/归档hash保持1db25bbdd2b15a9840a57028ae4e348a33679d60156a0876f91b96e96aa029ca。
- 生成Word的章节、原生公式、表和关键字段结构核对；原文、Word、提示词hash见project-document-audit.json。
- 治理与本地链接检查通过；唯一任务板增加V3-12，不改变原业务/研究任务的完成状态。

## 实际排版检查

先运行技能的render_docx.py；本机没有LibreOffice，日志明确报soffice.exe不存在。随后使用独立隐藏Word实例只读打开新文档，导出项目.local/project-handoff内临时PDF，再用文档工作环境的PDFium渲染页面；没有安装或使用桌面LibreOffice，也没有改原稿或Word安全设置。

逐页查看全部页面，修复目录孤页、架构示意跨页、公式与说明分离、长字段换行、接口索引列宽和孤立表头，保留表头重复与整行分页。最后表头修正后按页面PNG的SHA256对比已检查版本，只复看发生变化的页面；其余同字节页面沿用已完成的逐页检查。最终页数和变化页列表保存在project-document-layout.json。检查PDF与页面图片只作内部QA，不作为额外交付文件。

长标识符的字符级换行按[Microsoft WordWrap说明](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.wordwrap?view=openxml-3.0.1)设置，不插入不可见字符篡改可复制路径。正常接手代码和复制命令优先使用仓库Markdown。

## 接手方式

写本子的新窗口使用完整Word或主Markdown；开发队友在自己的clone使用prompts/06_CURRENT_PROJECT_HANDOFF.md，最后填写具体工作范围与验收结果。根README、AGENTS、当前实现状态和V3短交接均已增加总文档入口。主文档后续随实际实现更新，Word不要单独维护第二套事实。
