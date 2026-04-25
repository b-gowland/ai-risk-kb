// @ts-check

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'AI Risk Knowledge Base',
  tagline: 'A practitioner reference for understanding, assessing, and controlling AI risk — from board level to technical implementation.',
  favicon: 'img/favicon.ico',

  url: 'https://b-gowland.github.io',
  baseUrl: '/ai-risk-kb/',

  organizationName: 'b-gowland',
  projectName: 'ai-risk-kb',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  scripts: [
    {
      src: 'https://plausible.io/js/pa-KshwKmFS5HmfreqjImvCc.js',
      async: true,
    },
  ],

  headTags: [
    {
      tagName: 'script',
      attributes: {},
      innerHTML: `window.plausible=window.plausible||function(){(plausible.q=plausible.q||[]).push(arguments)},plausible.init=plausible.init||function(i){plausible.o=i||{}};plausible.init()`,
    },
  ],

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl: 'https://github.com/b-gowland/ai-risk-kb/tree/main/',
          showLastUpdateTime: false,
          showLastUpdateAuthor: false,
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/social-card.png',

      navbar: {
        title: 'AI Risk KB',
        logo: {
          alt: 'AI Risk Knowledge Base',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'riskSidebar',
            position: 'left',
            label: 'Risk Taxonomy',
          },
          {
            to: '/docs/how-to-use',
            label: 'How to Use',
            position: 'left',
          },
          {
            to: '/docs/about',
            label: 'About',
            position: 'left',
          },
          {
            label: 'Training Module',
            position: 'left',
            href: 'https://b-gowland.github.io/ai-risk-training/',
          },
          {
            href: 'https://github.com/b-gowland/ai-risk-kb',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },

      footer: {
        style: 'light',
        links: [
          {
            title: 'Taxonomy',
            items: [
              { label: 'A — Technical', to: '/docs/domain-a-technical/a1-hallucination' },
              { label: 'B — Governance', to: '/docs/domain-b-governance/b1-accountability' },
              { label: 'C — Security', to: '/docs/domain-c-security/c2-prompt-injection' },
              { label: 'D — Data', to: '/docs/domain-d-data/d1-training-data-quality' },
              { label: 'E — Fairness', to: '/docs/domain-e-fairness/e1-algorithmic-bias' },
              { label: 'F — Deployment', to: '/docs/domain-f-deployment/f1-automation-bias' },
              { label: 'G — Systemic', to: '/docs/domain-g-systemic/g4-ai-safety' },
            ],
          },
          {
            title: 'Resources',
            items: [
              { label: 'How to Use', to: '/docs/how-to-use' },
              { label: 'Schema Reference', to: '/docs/schema' },
              { label: 'Contributing', to: '/docs/contributing' },
              { label: 'Monitoring Sources', to: '/docs/monitoring-sources' },
              { label: 'Changelog', to: '/docs/changelog' },
            ],
          },
          {
            title: 'Frameworks Referenced',
            items: [
              { label: 'NIST AI RMF', href: 'https://www.nist.gov/itl/ai-risk-management-framework' },
              { label: 'EU AI Act', href: 'https://digital-strategy.ec.europa.eu/ai-act' },
              { label: 'MIT AI Risk Repository', href: 'https://airisk.mit.edu' },
              { label: 'OWASP LLM Top 10', href: 'https://owasp.org/www-project-top-10-for-large-language-model-applications' },
              { label: 'MITRE ATLAS', href: 'https://atlas.mitre.org' },
            ],
          },
          {
            title: 'Project',
            items: [
              { label: 'GitHub', href: 'https://github.com/b-gowland/ai-risk-kb' },
              { label: 'Report an Issue', href: 'https://github.com/b-gowland/ai-risk-kb/issues' },
              { label: 'Contribute', href: 'https://github.com/b-gowland/ai-risk-kb/blob/main/docs/contributing.md' },
            ],
          },
        ],
        copyright: `Open source AI risk reference. Content is provided for informational purposes — not legal or regulatory advice. Last updated ${new Date().getFullYear()}.`,
      },

      prism: {
        theme: require('prism-react-renderer').themes.github,
        darkTheme: require('prism-react-renderer').themes.dracula,
        additionalLanguages: ['python', 'yaml', 'bash', 'json'],
      },

      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },

      algolia: undefined,
    }),
};

module.exports = config;
