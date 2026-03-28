import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';

const DOMAINS = [
  {
    code: 'A',
    label: 'Technical',
    color: '#1a4f8a',
    desc: 'Hallucination, model drift, robustness failures, explainability gaps.',
    entries: 4,
    link: '/docs/domain-a-technical/a1-hallucination',
  },
  {
    code: 'B',
    label: 'Governance',
    color: '#2e7d32',
    desc: 'Accountability gaps, regulatory compliance, lifecycle governance, supply chain.',
    entries: 4,
    link: '/docs/domain-b-governance/b1-accountability',
  },
  {
    code: 'C',
    label: 'Security & Adversarial',
    color: '#b71c1c',
    desc: 'Data poisoning, prompt injection, model theft, deepfakes, AI-enabled attacks.',
    entries: 5,
    link: '/docs/domain-c-security/c2-prompt-injection',
  },
  {
    code: 'D',
    label: 'Data',
    color: '#e65100',
    desc: 'Training data quality, privacy and data protection, intellectual property.',
    entries: 3,
    link: '/docs/domain-d-data/d1-training-data-quality',
  },
  {
    code: 'E',
    label: 'Fairness & Social',
    color: '#6a1b9a',
    desc: 'Algorithmic bias and discrimination, harmful content, misinformation.',
    entries: 3,
    link: '/docs/domain-e-fairness/e1-algorithmic-bias',
  },
  {
    code: 'F',
    label: 'HCI & Deployment',
    color: '#00695c',
    desc: 'Automation bias, shadow AI, scope creep beyond intended use.',
    entries: 3,
    link: '/docs/domain-f-deployment/f1-automation-bias',
  },
  {
    code: 'G',
    label: 'Systemic & Macro',
    color: '#4e342e',
    desc: 'Concentration risk, environmental impact, workforce displacement, AI safety.',
    entries: 4,
    link: '/docs/domain-g-systemic/g4-ai-safety',
  },
];

function DomainCard({ code, label, color, desc, entries, link }) {
  return (
    <Link to={link} className="domain-card">
      <span className="domain-card-label" style={{ background: color }}>
        {code} — {label}
      </span>
      <h3>{label} Risks</h3>
      <p>{desc}</p>
      <p style={{ fontSize: '0.8rem', marginTop: '0.75rem', color: '#888' }}>
        {entries} risk {entries === 1 ? 'entry' : 'entries'}
      </p>
    </Link>
  );
}

export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title="AI Risk Knowledge Base"
      description="A practitioner reference for understanding, assessing, and controlling AI risk — from board level to technical implementation."
    >
      <div className="hero-banner">
        <h1>AI Risk Knowledge Base</h1>
        <p>
          A free, open-source reference for understanding, assessing, and controlling AI risk.
          Written for every level — from board to technical practitioner.
          17 risk categories across 7 domains, four layers of depth per entry.
        </p>
        <div className="hero-buttons">
          <Link className="button button--primary button--lg" to="/docs/how-to-use">
            Get started
          </Link>
          <Link className="button button--secondary button--lg" to="/docs/domain-c-security/c2-prompt-injection">
            See a full entry
          </Link>
          <Link className="button button--secondary button--lg" href="https://github.com/b-gowland/ai-risk-kb">
            GitHub
          </Link>
        </div>
      </div>

      <div style={{ background: 'var(--ifm-color-emphasis-100)', padding: '2rem', textAlign: 'center' }}>
        <p style={{ maxWidth: 700, margin: '0 auto', fontSize: '0.95rem', lineHeight: 1.7 }}>
          Each entry covers four layers: a plain-English <strong>executive card</strong>,
          a <strong>practitioner overview</strong> with controls ownership and go-live criteria,
          an <strong>actionable controls detail</strong>, and a <strong>technical implementation</strong> guide with code examples.
          Built for use alongside your own risk assessments — not as a substitute for them.
        </p>
      </div>

      <div className="domain-grid">
        {DOMAINS.map((d) => <DomainCard key={d.code} {...d} />)}
      </div>

      <div style={{ textAlign: 'center', padding: '2rem', borderTop: '1px solid var(--ifm-color-emphasis-200)' }}>
        <p style={{ fontSize: '0.9rem', color: 'var(--ifm-color-emphasis-600)', maxWidth: 600, margin: '0 auto' }}>
          Open source under MIT licence. Content is provided for informational purposes.
          Not legal, regulatory, or professional advice.
          <br />
          Basis: MIT AI Risk Repository · NIST AI RMF 1.0 & AI 600-1 · EU AI Act · OWASP LLM Top 10 · Documented AI incidents.
        </p>
      </div>
    </Layout>
  );
}
