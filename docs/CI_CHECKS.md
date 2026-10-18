# 自动化检查与证据范围

Application checks在功能分支push和PR运行Linux检查：锁定Python/Node环境，Python测试，契约/治理，ESLint、前端单测与生产构建。重新生成Pydantic、实际OpenAPI和TS后检查Git无差异；不能只改Schema而漏提交消费者。

新增浏览器烟测在同一隔离环境安装项目内Chromium，执行“单点诊断”和“生产构建只允许本机请求”两条真实流程。安装方式参考[Playwright官方CI说明](https://playwright.dev/docs/ci-intro)。它不等于本机完整E2E套件；本机全套仍用scripts/verify.py --browser。

烟测结果写入全新的.local/ci-artifacts/browser-smoke.json，并通过[官方upload-artifact](https://github.com/actions/upload-artifact)保留7天；失败时附带本轮frontend/test-results中的trace/截图。只上传此专用结果与新测试目录，不上传runtime、环境变量、数据库、凭据或工作区其他项目。仓库历史截图不作为这次CI新生成的证据。

运行状态由GitHub Actions实际结果决定，不因已推送或本机通过就写远端成功。evidence/verification/github-ci.json记录逐提交查询结果，保留历史失败；后续提交不能自动继承旧CI结论。

本机可用同一Node入口验证筛选参数：

```powershell
node frontend/scripts/run-e2e.mjs --grep '单点诊断|生产构建'
```

自定义YUANHANG_E2E_REPORT只改变JSON报告目标。测试仍用独立8011/5174和.local/e2e-runtime，不访问演示runtime。常规完整验收不设此变量时，将记录evidence/browser/e2e-results.json；定向验收记录e2e-targeted-results.json。
