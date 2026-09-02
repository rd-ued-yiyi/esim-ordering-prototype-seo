# eSIM 订购流程原型（SEO 版）

KKday eSIM B2C 主题及订购流程改造的**可点击原型**，用于可用性测试。移动端，按 Figma 高保真还原，视觉基于 KKday Web Design System tokens。

线上（GitHub Pages）：https://rd-ued-yiyi.github.io/esim-ordering-prototype-seo/

本仓库是 [esim-ordering-prototype](https://github.com/rd-ued-yiyi/esim-ordering-prototype) 在 `40fc6ed` 处的独立副本，用于 SEO 方向的改造，与原型主线互不影响。

## 结构

- `index.html` — 自包含成品（资产全内联，直接部署即可），由构建脚本产出
- `src/template.html` — 可编辑模板，用 `{{TOKEN}}` 占位资产
- `build.py` — 把 `assets/` 内的 SVG/PNG 内联进模板，产出 `index.html`
- `assets/` — 从 Figma / 设计系统导出的图标、pictogram、hero 插画

## 更新

```bash
python3 build.py       # 重新生成 index.html
git add -A && git commit -m "update" && git push   # 触发 Pages 重新部署
```

## 进度

- [x] 第 1 页：主题落地页（hero / 目的地选择 / 为什么选 KKday / 安装指南 / FAQ）
- [x] 第 2 页：目的地页（天数/流量选择、选择目的地 modal）
- [x] 第 3 页：套餐列表页（条件 chips / 筛选 / 排序 / 仿真卡片）
- [x] 套餐详情 Full-screen Modal（锚点 tab / 基本信息 / 评论区锚定 / 图文说明）
- [ ] 订购流程页面
