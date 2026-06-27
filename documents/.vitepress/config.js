import { withMermaid } from "vitepress-plugin-mermaid";

export default withMermaid({
  base: '/pyClickMouse/',
  head: [['link', { rel: 'icon', href: '/imgs/icons/icon.ico' }]],
  markdown: {
    emoji: {
      enabled: 'off',
    },
  },

  // 主题配置
  themeConfig: {
    logo: '/imgs/icons/icon.ico',
    siteTitle: 'Clickmouse docs',

    // 搜索功能
    search: {
      provider: 'local',
      options: {
        locales: {
          'zh-CN': {
            translations: {
              button: {
                buttonText: '搜索',
                buttonAriaLabel: '搜索',
              },
              modal: {
                noResultsText: '无法找到相关结果',
                resetButtonTitle: '清除查询条件',
                footer: {
                  selectText: '选择',
                  navigateText: '切换',
                  closeText: '关闭',
                },
              },
            },
          },
          en: {
            translations: {
              button: {
                buttonText: 'Search',
                buttonAriaLabel: 'Search',
              },
              modal: {
                noResultsText: 'No results found',
                resetButtonTitle: 'Clear query',
                footer: {
                  selectText: 'to select',
                  navigateText: 'to navigate',
                  closeText: 'to close',
                },
              },
            },
          },
        },
      },
    },
  },

  // 多语言配置
  locales: {
    en: {
      title: 'Clickmouse docs',
      description: 'Clickmouse docs powered by vitepress',
      label: 'English',
      lang: 'en',
      link: '/en/',
      themeConfig: {
        outlineTitle: 'On this page',
        lastUpdatedText: 'Last Updated',
        editLink: {
          pattern:
            'https://github.com/xystudiocode/pyClickMouse/tree/main/documents/:path',
          text: 'Edit this page',
        },
        docFooter: {
          prev: 'Previous',
          next: 'Next',
        },
        notFound: {
          title: 'PAGE NOT FOUND',
          quote:
            "But if you don't change your direction, and if you keep looking, you may end up where you are heading.",
          linkText: 'Take me home',
        },
        // 配置主题
        lightModeSwitchTitle: 'Switch to light mode',
        darkModeSwitchTitle: 'Switch to dark mode',
        // 社交链接
        socialLinks: [
          { icon: 'github', link: 'https://github.com/xystudiocode/pyClickMouse' },
          { icon: 'gitee', link: 'https://gitee.com/xystudio889/pyClickMouse' },
        ],
        sidebar: {
          '/en/guide/': [
            {
              text: 'Guide',
              items: [
                { text: 'Introduction', link: '/en/guide/' },
                { text: 'Getting Started', link: '/en/guide/getting-started' },
                { text: 'FAQ', link: '/en/guide/faq',},
                { text: 'Version Naming', link: '/en/guide/version-naming',},
                { text: 'License', link: '/en/guide/license',},
              ],
            },
          ],
          '/en/updatelog/': [
            {
              text: 'Update log',
              items: [
                {
                  text: 'Final',
                  collapsed: true,
                  items: [
                    {
                      text: 'v3.x.x.x',
                      collapsed: true,
                      items: [
                        {
                          text: '3.2.3.22',
                          link: '/en/updatelog/final/3/32322',
                        },
                        {
                          text: '3.2.2.21',
                          link: '/en/updatelog/final/3/32221',
                        },
                        {
                          text: '3.2.1.20',
                          link: '/en/updatelog/final/3/32120',
                        },
                        {
                          text: '3.2.0.19',
                          link: '/en/updatelog/final/3/32019',
                        },
                        {
                          text: '3.1.3.18',
                          link: '/en/updatelog/final/3/31318',
                        },
                        {
                          text: '3.1.2.17',
                          link: '/en/updatelog/final/3/31217',
                        },
                        {
                          text: '3.1.1.16',
                          link: '/en/updatelog/final/3/31116',
                        },
                        {
                          text: '3.1.0.15',
                          link: '/en/updatelog/final/3/31015',
                        },
                        {
                          text: '3.0.3.14',
                          link: '/en/updatelog/final/3/30314',
                        },
                        {
                          text: '3.0.2.13',
                          link: '/en/updatelog/final/3/30213',
                        },
                        {
                          text: '3.0.1.12',
                          link: '/en/updatelog/final/3/30112',
                        },
                        {
                          text: '3.0.0.11',
                          link: '/en/updatelog/final/3/30011',
                        },
                      ],
                    },
                    {
                      text: 'v2.x.x.x',
                      collapsed: true,
                      items: [
                        {
                          text: '2.2.3.10',
                          link: '/en/updatelog/final/2/22310',
                        },
                        {
                          text: '2.2.2.9',
                          link: '/en/updatelog/final/2/2229',
                        },
                        {
                          text: '2.2.1.8',
                          link: '/en/updatelog/final/2/2218',
                        },
                        {
                          text: '2.2.0.7',
                          link: '/en/updatelog/final/2/2207',
                        },
                        {
                          text: '2.1.1.6',
                          link: '/en/updatelog/final/2/2116',
                        },
                        {
                          text: '2.1.0.5',
                          link: '/en/updatelog/final/2/2105',
                        },
                        {
                          text: '2.0.0.4',
                          link: '/en/updatelog/final/2/2004',
                        },
                      ],
                    },
                    {
                      text: 'v1.x.x.x',
                      collapsed: true,
                      items: [
                        {
                          text: '1.0.2.3',
                          link: '/en/updatelog/final/1/1023',
                        },
                        {
                          text: '1.0.2.2',
                          link: '/en/updatelog/final/1/1022',
                        },
                        {
                          text: '1.0.1.1',
                          link: '/en/updatelog/final/1/1011',
                        },
                        {
                          text: '1.0.0.0',
                          link: '/en/updatelog/final/1/1000',
                        },
                      ],
                    },
                  ],
                },
                {
                  text: 'Preview',
                  collapsed: true,
                  items: [
                    {
                      text: 'v3.x.x.x',
                      collapsed: true,
                      items: [
                        {
                          text: '3.3.0.23alpha6',
                          link: '/en/updatelog/beta/3/33023a6',
                        },
                        {
                          text: '3.3.0.23alpha5',
                          link: '/en/updatelog/beta/3/33023a5',
                        },
                        {
                          text: '3.3.0.23alpha4',
                          link: '/en/updatelog/beta/3/33022a4',
                        },
                        {
                          text: '3.3.0.23alpha2',
                          link: '/en/updatelog/beta/3/32120a2',
                        },
                        {
                          text: '3.3.0.23alpha1',
                          link: '/en/updatelog/beta/3/32120a1',
                        },
                        {
                          text: '3.2.0.19rc3',
                          link: '/en/updatelog/beta/3/32019rc3',
                        },
                        {
                          text: '3.2.0.19rc2',
                          link: '/en/updatelog/beta/3/32019rc2',
                        },
                        {
                          text: '3.2.0.19rc1',
                          link: '/en/updatelog/beta/3/32019rc1',
                        },
                        {
                          text: '3.2.0.19beta11',
                          link: '/en/updatelog/beta/3/32019b11',
                        },
                        {
                          text: '3.2.0.19beta10',
                          link: '/en/updatelog/beta/3/32019b10',
                        },
                        {
                          text: '3.2.0.19beta9',
                          link: '/en/updatelog/beta/3/32019b9',
                        },
                        {
                          text: '3.2.0.18beta8',
                          link: '/en/updatelog/beta/3/32018b8',
                        },
                        {
                          text: '3.2.0.18beta5',
                          link: '/en/updatelog/beta/3/32018b5',
                        },
                        {
                          text: '3.2.0.18beta4',
                          link: '/en/updatelog/beta/3/32018b4',
                        },
                        {
                          text: '3.1.2.17beta3',
                          link: '/en/updatelog/beta/3/31217b3',
                        },
                        {
                          text: '3.1.2.17beta1',
                          link: '/en/updatelog/beta/3/31217b1',
                        },
                        {
                          text: '3.1.0.15beta3',
                          link: '/en/updatelog/beta/3/31015b3',
                        },
                        {
                          text: '3.1.0.15beta2',
                          link: '/en/updatelog/beta/3/31015b2',
                        },
                        {
                          text: '3.1.0.15beta1',
                          link: '/en/updatelog/beta/3/31015b1',
                        },
                        {
                          text: '3.1.0.15.dev0',
                          link: '/en/updatelog/beta/3/31015dev0',
                        },
                        {
                          text: '3.0.2.13rc1',
                          link: '/en/updatelog/beta/3/30213rc1',
                        },
                        {
                          text: '3.0.1.12rc1',
                          link: '/en/updatelog/beta/3/30112rc1',
                        },
                        {
                          text: '3.0.0.11rc1',
                          link: '/en/updatelog/beta/3/30011rc1',
                        },
                        {
                          text: '3.0.0.11alpha3',
                          link: '/en/updatelog/beta/3/30011a3',
                        },
                        {
                          text: '3.0.0.11alpha2',
                          link: '/en/updatelog/beta/3/30011a2',
                        },
                        {
                          text: '3.0.0.11alpha1',
                          link: '/en/updatelog/beta/3/30011a1',
                        },
                        {
                          text: '3.0.0.11.dev4',
                          link: '/en/updatelog/beta/3/30011dev4',
                        },
                        {
                          text: '3.0.0.11.dev3',
                          link: '/en/updatelog/beta/3/30011dev3',
                        },
                        {
                          text: '3.0.0.11.dev1',
                          link: '/en/updatelog/beta/3/30011dev1',
                        },
                      ],
                    },
                  ],
                },
              ],
            },
          ],
          '/en/features/': [
            {
              text: 'Features',
              items: [
                {
                  text: 'Introduction',
                  link: '/en/features/',
                },
                {
                  text: 'Clean cache',
                  link: '/en/features/cleancache',
                },
                {
                  text: 'Settings',
                  link: '/en/features/settings',
                },
                {
                  text: 'Update',
                  link: '/en/features/update',
                },
                {
                  text: 'Help',
                  link: '/en/features/help',
                },
                {
                  text: 'clickclean',
                  link: '/en/features/clickclean',
                },
                {
                  text: 'Extensions',
                  collapsed: true,
                  items: [{ text: 'Introducing', link: '/en/features/extensions' }, { text: 'Repair', link: '/en/features/extensions/repair' }],
                },
              ],
            },
          ],
          '/en/develop': [
            {
            text: 'Developers',
            items: [
              {
                text: 'Introduction',
                link: '/en/develop/index',
              },
              {
                text: 'Dependencies',
                link: '/en/develop/dependencies',
              },
              {
                  text: 'Clickmouse library usage',
                  collapsed: true,
                  items: [
                    {
                      text: 'Introduction',
                      link: '/en/develop/clicker/index',
                    },
                    {
                      text: 'Calling using Python/pyd',
                      link: '/en/develop/clicker/python',
                    },
                    {
                      text: 'Calling using C++/dll',
                      link: '/en/develop/clicker/cpp',
                    }
                  ],
                },
                {
                  text: 'Contributing',
                  collapsed: true,
                  items: [
                    {
                      text: 'Contributing clickmouse',
                      link: '/en/develop/contributing/github',
                    },
                    {
                      text: 'Configuration development environment',
                      link: '/en/develop/contributing/configuration',
                    },
                    {
                      text: 'Documentation development',
                      link: '/en/develop/contributing/doc',
                    },
                    {
                      text: 'Issue template',
                      link: '/en/develop/contributing/issue_template'
                    },
                    {
                      text: 'Security policy',
                      link: '/en/develop/contributing/security'
                    },
                    {
                      text: 'License',
                      link: '/en/develop/contributing/license'
                    }
                  ],
                },
              ],
            },
          ],
        },
        nav: [
          { text: 'Home', link: '/en/' },
          { text: 'Guide', link: '/en/guide/' },
          { text: 'Features', link: '/en/features/' },
          { text: 'Update log', link: '/en/updatelog/' },
          { text: 'Developers', link: '/en/develop/'}
        ],
        returnToTopLabel: 'Return to top',
      },
    },
    'zh-CN': {
      label: '简体中文',
      description: '基于 vitepress 搭建的 Clickmouse 文档',
      title: 'Clickmouse 文档 | VitePress',
      link: '/zh-CN/',
      lang: 'zh-CN',
      themeConfig: {
        siteTitle: 'Clickmouse 文档',
        returnToTopLabel: '返回顶部',
        outlineTitle: '本页目录',
        lastUpdatedText: '最后更新',
        sidebarMenuLabel: '目录',
        editLink: {
          pattern:
            'https://github.com/xystudiocode/pyClickMouse/tree/main/documents/:path',
          text: '编辑此页',
        },
        notFound: {
          title: '页面不存在',
          quote: '只要不改变你的方向，一直寻找，最终会找到你所寻找的目标',
          linkText: '返回首页',
        },
        // 配置主题
        lightModeSwitchTitle: '切换到浅色模式',
        darkModeSwitchTitle: '切换到深色模式',
        darkModeSwitchLabel: '主题',
        // 社交链接
        socialLinks: [
          { icon: 'github', link: 'https://github.com/xystudiocode/pyClickMouse'},
          { icon: 'gitee', link: 'https://gitee.com/xystudio889/pyClickMouse' },
        ],
        nav: [
          { text: '首页', link: '/zh-CN/' },
          { text: '指南', link: '/zh-CN/guide/' },
          { text: '功能', link: '/zh-CN/features/' },
          { text: '更新日志', link: '/zh-CN/updatelog/' },
          { text: '开发者', link: '/zh-CN/develop/' }
        ],
        docFooter: {
          prev: '上一页',
          next: '下一页',
        },
        footer: {
          message: '本软件使用MIT协议开源',
          copyright: '© 2025-现在 xystudio版权所有',
        },
        sidebar: {
          '/zh-CN/guide/': [
            {
              text: '指南',
              items: [
                { text: '介绍', link: '/zh-CN/guide/' },
                { text: '开始使用', link: '/zh-CN/guide/getting-started' },
                { text: 'FAQ', link: '/zh-CN/guide/faq',},
                { text: '版本命名', link: '/zh-CN/guide/version-naming',},
                { text: '用户协议', link: '/zh-CN/guide/license',},
              ],
            },
          ],
          '/zh-CN/updatelog/': [
            {
              text: '发行日志',
              items: [
                {
                  text: '正式版',
                  collapsed: true,
                  items: [
                    {
                      text: 'v3.x.x.x',
                      collapsed: true,
                      items: [
                        {
                          text: '3.2.3.22',
                          link: '/zh-CN/updatelog/final/3/32322',
                        },
                        {
                          text: '3.2.2.21',
                          link: '/zh-CN/updatelog/final/3/32221',
                        },
                        {
                          text: '3.2.1.20',
                          link: '/zh-CN/updatelog/final/3/32120'
                        },
                        {
                          text: '3.2.0.19',
                          link: '/zh-CN/updatelog/final/3/32019',
                        },
                        {
                          text: '3.1.3.18',
                          link: '/zh-CN/updatelog/final/3/31318',
                        },
                        {
                          text: '3.1.2.17',
                          link: '/zh-CN/updatelog/final/3/31217',
                        },
                        {
                          text: '3.1.1.16',
                          link: '/zh-CN/updatelog/final/3/31116',
                        },
                        {
                          text: '3.1.0.15',
                          link: '/zh-CN/updatelog/final/3/31015',
                        },
                        {
                          text: '3.0.3.14',
                          link: '/zh-CN/updatelog/final/3/30314',
                        },
                        {
                          text: '3.0.2.13',
                          link: '/zh-CN/updatelog/final/3/30213',
                        },
                        {
                          text: '3.0.1.12',
                          link: '/zh-CN/updatelog/final/3/30112',
                        },
                        {
                          text: '3.0.0.11',
                          link: '/zh-CN/updatelog/final/3/30011',
                        },
                      ],
                    },
                    {
                      text: 'v2.x.x.x',
                      collapsed: true,
                      items: [
                        {
                          text: '2.2.3.10',
                          link: '/zh-CN/updatelog/final/2/22310',
                        },
                        {
                          text: '2.2.2.9',
                          link: '/zh-CN/updatelog/final/2/2229',
                        },
                        {
                          text: '2.2.1.8',
                          link: '/zh-CN/updatelog/final/2/2218',
                        },
                        {
                          text: '2.2.0.7',
                          link: '/zh-CN/updatelog/final/2/2207',
                        },
                        {
                          text: '2.1.1.6',
                          link: '/zh-CN/updatelog/final/2/2116',
                        },
                        {
                          text: '2.1.0.5',
                          link: '/zh-CN/updatelog/final/2/2105',
                        },
                        {
                          text: '2.0.0.4',
                          link: '/zh-CN/updatelog/final/2/2004',
                        },
                      ],
                    },
                    {
                      text: 'v1.x.x.x',
                      collapsed: true,
                      items: [
                        {
                          text: '1.0.2.3',
                          link: '/zh-CN/updatelog/final/1/1023',
                        },
                        {
                          text: '1.0.2.2',
                          link: '/zh-CN/updatelog/final/1/1022',
                        },
                        {
                          text: '1.0.1.1',
                          link: '/zh-CN/updatelog/final/1/1011',
                        },
                        {
                          text: '1.0.0.0',
                          link: '/zh-CN/updatelog/final/1/1000',
                        },
                      ],
                    },
                  ],
                },
                {
                  text: '预览版',
                  collapsed: true,
                  items: [
                    {
                      text: 'v3.x.x.x',
                      collapsed: true,
                      items: [
                        {
                          text: '3.3.0.23alpha6',
                          link: '/zh-CN/updatelog/beta/3/33023a6',
                        },
                        {
                          text: '3.3.0.23alpha5',
                          link: '/zh-CN/updatelog/beta/3/33023a5',
                        },
                        {
                          text: '3.3.0.22alpha4',
                          link: '/zh-CN/updatelog/beta/3/33022a4',
                        },
                        {
                          text: '3.2.1.20alpha2',
                          link: '/zh-CN/updatelog/beta/3/32120a2',
                        },
                        {
                          text: '3.2.1.20alpha1',
                          link: '/zh-CN/updatelog/beta/3/32120a1',
                        },
                        {
                          text: '3.2.0.19rc3',
                          link: '/zh-CN/updatelog/beta/3/32019rc3',
                        },
                        {
                          text: '3.2.0.19rc2',
                          link: '/zh-CN/updatelog/beta/3/32019rc2',
                        },
                        {
                          text: '3.2.0.19rc1',
                          link: '/zh-CN/updatelog/beta/3/32019rc1',
                        },
                        {
                          text: '3.2.0.19beta11',
                          link: '/zh-CN/updatelog/beta/3/32019b11',
                        },
                        {
                          text: '3.2.0.19beta10',
                          link: '/zh-CN/updatelog/beta/3/32019b10',
                        },
                        {
                          text: '3.2.0.19beta9',
                          link: '/zh-CN/updatelog/beta/3/32019b9',
                        },
                        {
                          text: '3.2.0.18beta8',
                          link: '/zh-CN/updatelog/beta/3/32018b8',
                        },
                        {
                          text: '3.2.0.18beta5',
                          link: '/zh-CN/updatelog/beta/3/32018b5',
                        },
                        {
                          text: '3.2.0.18beta4',
                          link: '/zh-CN/updatelog/beta/3/32018b4',
                        },
                        {
                          text: '3.1.2.17beta3',
                          link: '/zh-CN/updatelog/beta/3/31217b3',
                        },
                        {
                          text: '3.1.2.17beta1',
                          link: '/zh-CN/updatelog/beta/3/31217b1',
                        },
                        {
                          text: '3.1.0.15beta3',
                          link: '/zh-CN/updatelog/beta/3/31015b3',
                        },
                        {
                          text: '3.1.0.15beta2',
                          link: '/zh-CN/updatelog/beta/3/31015b2',
                        },
                        {
                          text: '3.1.0.15beta1',
                          link: '/zh-CN/updatelog/beta/3/31015b1',
                        },
                        {
                          text: '3.1.0.15.dev0',
                          link: '/zh-CN/updatelog/beta/3/31015dev0',
                        },
                        {
                          text: '3.0.2.13rc1',
                          link: '/zh-CN/updatelog/beta/3/30213rc1',
                        },
                        {
                          text: '3.0.1.12rc1',
                          link: '/zh-CN/updatelog/beta/3/30112rc1',
                        },
                        {
                          text: '3.0.0.11rc1',
                          link: '/zh-CN/updatelog/beta/3/30011rc1',
                        },
                        {
                          text: '3.0.0.11alpha3',
                          link: '/zh-CN/updatelog/beta/3/30011a3',
                        },
                        {
                          text: '3.0.0.11alpha2',
                          link: '/zh-CN/updatelog/beta/3/30011a2',
                        },
                        {
                          text: '3.0.0.11alpha1',
                          link: '/zh-CN/updatelog/beta/3/30011a1',
                        },
                        {
                          text: '3.0.0.11.dev4',
                          link: '/zh-CN/updatelog/beta/3/30011dev4',
                        },
                        {
                          text: '3.0.0.11.dev3',
                          link: '/zh-CN/updatelog/beta/3/30011dev3',
                        },
                        {
                          text: '3.0.0.11.dev1',
                          link: '/zh-CN/updatelog/beta/3/30011dev1',
                        },
                      ],
                    },
                  ],
                },
              ],
            },
          ],
          '/zh-CN/features/': [
            {
              text: '功能',
              items: [
                {
                  text: '介绍',
                  link: '/zh-CN/features/',
                },
                {
                  text: '清理缓存',
                  link: '/zh-CN/features/cleancache',
                },
                {
                  text: '设置',
                  link: '/zh-CN/features/settings',
                },
                {
                  text: '更新',
                  link: '/zh-CN/features/update',
                },
                {
                  text: '帮助',
                  link: '/zh-CN/features/help',
                },
                {
                  text: 'clickclean',
                  link: '/zh-CN/features/clickclean',
                },
                {
                  text: '扩展',
                  collapsed: true,
                  items: [{ text: '介绍', link: '/zh-CN/features/extensions' }],
                },
              ],
            },
          ],
          '/zh-CN/develop': [
            {
            text: '开发人员',
            items: [
              {
                text: '介绍',
                link: '/zh-CN/develop/index',
              },
              {
                text: '依赖',
                link: '/zh-CN/develop/dependencies',
              },
              {
                  text: 'clickmouse库调用',
                  collapsed: true,
                  items: [
                    {
                      text: '介绍',
                      link: '/zh-CN/develop/clicker/index',
                    },
                    {
                      text: '基于python/pyd的调用',
                      link: '/zh-CN/develop/clicker/python',
                    },
                    {
                      text: '基于C++/dll的调用',
                      link: '/zh-CN/develop/clicker/cpp',
                    }
                  ],
                },
                {
                  text: '参与协作',
                  collapsed: true,
                  items: [
                    {
                      text: '协作clickmouse',
                      link: '/zh-CN/develop/contributing/github',
                    },
                    {
                      text: '配置开发环境',
                      link: '/zh-CN/develop/contributing/configuration',
                    },
                    {
                      text: '文档协作',
                      link: '/zh-CN/develop/contributing/doc',
                    },
                    {
                      text: 'issue 模板',
                      link: '/zh-CN/develop/contributing/issue_template'
                    },{
                      text: '安全报告',
                      link: '/zh-CN/develop/contributing/security'
                    },
                    {
                      text: '软件协议',
                      link: '/zh-CN/develop/contributing/license'
                    }
                  ],
                },
              ],
            },
          ],
        },
      },
    },
  },
});
