import { defineConfig } from 'vitepress'

export default defineConfig({
  lang: 'zh-CN',
  title: 'ApeHub 技术文档',
  description: 'ApeAdmin / FastAPI 插件平台与 ApeHub 市场开发文档',
  base: '/apehub-web/docs-portal/',
  outDir: '../../static/docs-portal',
  cleanUrls: true,
  lastUpdated: true,
  head: [
    ['script', {}, `(function () {
      try {
        var theme = localStorage.getItem('ape-theme') || 'dark'
        document.documentElement.classList.toggle('dark', theme === 'dark')
        localStorage.setItem('vitepress-theme-appearance', theme)
      } catch (error) {}
    })()`],
  ],
  themeConfig: {
    logo: '../assets/logo.png',
    nav: [
      { text: '平台指南', link: '/guide/overview' },
      { text: '插件市场文档', link: '/marketplace/submission' },
    ],
    sidebar: [
      {
        text: 'ApeAdmin 底座',
        items: [
          { text: '平台概览', link: '/guide/overview' },
          { text: '架构与请求链路', link: '/guide/architecture' },
          { text: '本地运行', link: '/guide/quickstart' },
          { text: 'API 约定', link: '/guide/api' },
          { text: '运维与排查', link: '/guide/operations' },
          { text: '安全与权限', link: '/guide/security' },
          { text: '插件生命周期', link: '/guide/plugin-lifecycle' },
        ],
      },
      {
        text: '插件市场',
        items: [
          { text: '提交与 AI 分析', link: '/marketplace/submission' },
          { text: '版本与审核', link: '/marketplace/versions' },
          { text: 'USDT 支付与结算', link: '/marketplace/settlement' },
        ],
      },
    ],
    search: { provider: 'local' },
    outline: { level: [2, 3], label: '本页目录' },
    docFooter: { prev: '上一页', next: '下一页' },
    lastUpdated: { text: '最后更新于' },
    footer: { message: 'ApeHub 插件生态', copyright: 'ApeAdmin' },
  },
})
