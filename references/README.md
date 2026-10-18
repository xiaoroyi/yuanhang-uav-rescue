# 来源与使用方式

本目录归档用户提供的原始资料和数模回归依据，不能当作新系统运行输出。精确来源、体积与 SHA-256 见 SOURCES.json，所有原件按字节复制，未修改外部源目录。

`.gitattributes` 对 references 关闭换行转换，保证 Windows/Linux 克隆后的原件哈希一致。不要对归档文件统一格式化或清理原有Markdown空格。

| 内容 | 路径 | 用途 |
|---|---|---|
| 详细开发 Word | source/development-plan.docx | 原始需求依据 |
| Word 可检索文本 | source/development-plan.extracted.md | 便于 Codex 阅读；表格转文本，公式/图片以原件为准 |
| 初步讨论 | source/product-discussion.txt | 背景资料；旧三人/按日安排已被当前规范覆盖 |
| 原始13文件对接包 | source/original-handoff.zip | 保留未适配原文；活动规范已统一两人 |
| 数模原题、论文、答案 | modeling/problem.docx、paper.pdf、answers.xlsx | 历史研究与回归依据 |
| 正式提交18份源码 | modeling/submitted-code/ | 精选算法源码，不含依赖环境 |
| 较完整发布包 | modeling/verified-release-code-and-results.zip | 复现时按内部清单选择，不直接解压运行 |
| 五张输入表、DEM mat/tif | modeling/data/ | 保留基准必要输入；未复制整套 GIS 数据 |
| 发布清单/主方案指标/核验 | modeling/release/ | 区分正式版本与旧探索结果 |

原 Word 的官方截止、字数、匿名与复用条款为来源转述；本轮未取得比赛指南原件，也未联网核验官方最新通知。正式交付时由 S-04 核对并留证，不将来源文档的“已核验”当作本轮已核验。

论文首封面含培养单位、参赛号及作者身份。仅作内部研究资料；`submission/` 匿名包必须独立构建，不能把 references 整目录直接打包交赛。原代码与数据使用权、第三方许可证尚待核实，不自动附加开源许可证。
