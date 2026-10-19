# 当前项目文档

主源为 [项目实际实现与协作对接总文档](../PROJECT_DOSSIER.md)，Word版为本目录的`援航项目实际实现与协作对接总文档.docx`。背景、数模继承、详细算法、前后端、功能、实际证据、原方案差异、未完成内容以及无记忆Codex的阅读顺序与提示词集中在同一文档中。

接手开发使用Markdown和 [提示词](../../prompts/06_CURRENT_PROJECT_HANDOFF.md)，写本子或交流可以使用Word。两种格式现为1.3/V4，绑定feat/mission-command-v4完整交付及参考包修订；Word由Markdown生成，不单独维护事实。第24章说明本地EOH、案例资产和接入；第25章现已完整纳入2026年10月19日晚v6批次16套600秒独立方案、四组结果、耗时、能耗分项、SOC/截止/通信核验与引用限制，研究数据采用最新完成批次。可复用的[16方案原始精度总表](contest-baselines-v6/16方案完整结果.csv)、[64检查点](contest-baselines-v6/64检查点结果.csv)与[引用说明](contest-baselines-v6/结果与引用说明.md)供写本子/PPT使用。第19.5节说明演示包。内部完整文档与提示词不放入师兄演示包，对外另用[图文演示指南](../PROJECT_DEMO_GUIDE.md)。本对接入口只呈现最终实验方案和结果。

生成器：`scripts/build_project_dossier.py`，使用文档工作环境的python-docx。生成后需实际渲染并查看页面，检查公式、跨页表格和路径换行；不能只看Word结构成功就宣布版面合格。当前内部检查记录在`evidence/experience-v4/DOCUMENT_REVIEW.md`，V3记录保留历史范围。
