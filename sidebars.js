/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  riskSidebar: [
    {
      type: 'doc',
      id: 'how-to-use',
      label: 'How to Use This Resource',
    },
    {
      type: 'category',
      label: 'A — Technical Risks',
      collapsed: false,
      items: [
        'domain-a-technical/a1-hallucination',
        'domain-a-technical/a2-model-drift',
        'domain-a-technical/a3-robustness',
        'domain-a-technical/a4-explainability',
      ],
    },
    {
      type: 'category',
      label: 'B — Governance Risks',
      collapsed: true,
      items: [
        'domain-b-governance/b1-accountability',
        'domain-b-governance/b2-regulatory-compliance',
        'domain-b-governance/b3-lifecycle-governance',
        'domain-b-governance/b4-supply-chain',
      ],
    },
    {
      type: 'category',
      label: 'C — Security & Adversarial',
      collapsed: true,
      items: [
        'domain-c-security/c1-data-poisoning',
        'domain-c-security/c2-prompt-injection',
        'domain-c-security/c3-model-theft',
        'domain-c-security/c4-deepfakes',
        'domain-c-security/c5-ai-cyber-attacks',
      ],
    },
    {
      type: 'category',
      label: 'D — Data Risks',
      collapsed: true,
      items: [
        'domain-d-data/d1-training-data-quality',
        'domain-d-data/d2-privacy',
        'domain-d-data/d3-intellectual-property',
      ],
    },
    {
      type: 'category',
      label: 'E — Fairness & Social',
      collapsed: true,
      items: [
        'domain-e-fairness/e1-algorithmic-bias',
        'domain-e-fairness/e2-harmful-content',
        'domain-e-fairness/e3-misinformation',
      ],
    },
    {
      type: 'category',
      label: 'F — HCI & Deployment',
      collapsed: true,
      items: [
        'domain-f-deployment/f1-automation-bias',
        'domain-f-deployment/f2-shadow-ai',
        'domain-f-deployment/f3-scope-creep',
      ],
    },
    {
      type: 'category',
      label: 'G — Systemic & Macro',
      collapsed: true,
      items: [
        'domain-g-systemic/g1-concentration-risk',
        'domain-g-systemic/g2-environmental-impact',
        'domain-g-systemic/g3-workforce-displacement',
        'domain-g-systemic/g4-ai-safety',
      ],
    },
    {
      type: 'category',
      label: 'Reference',
      collapsed: true,
      items: [
        'about',
        'schema',
        'monitoring-sources',
        'contributing',
        'changelog',
      ],
    },
  ],
};

module.exports = sidebars;
