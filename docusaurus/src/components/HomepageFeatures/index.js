import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Spec-Driven Content',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        All content is generated from explicit specifications by AI agents,
        ensuring consistency, accuracy, and traceability. The Constitution
        and Specification files are the source of truth.
      </>
    ),
  },
  {
    title: 'Deep Technical Coverage',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        Four comprehensive chapters covering Physical AI foundations, ROS 2
        architecture, simulation and digital twins, and cutting-edge
        Vision-Language-Action systems.
      </>
    ),
  },
  {
    title: 'AI-Powered Learning',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        An embedded RAG chatbot answers your questions using only textbook
        content—no hallucination, proper citations, and explicit refusals
        for out-of-scope queries.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
