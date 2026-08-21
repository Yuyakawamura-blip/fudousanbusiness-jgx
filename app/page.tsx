import { siteConfig } from "./site-config";

const concerns = [
  "相続する山について、何から確認すればよいか分からない",
  "遠方に住んでいて、手入れや様子の確認が難しい",
  "山の場所、境界、共有者のことがはっきりしない",
  "持ち続けること、管理すること、売却することの選択に迷っている",
];
const interviewItems = [
  "森林・里山の所在地と、相談者との関係",
  "相続前・相続後の状況、登記や共有の有無",
  "現在の管理状況と、今後についてのお考え",
  "お手元にある登記資料・図面・写真など",
];
const steps = [
  [
    "01",
    "まず、お話をうかがいます",
    "対面・電話・オンラインで、今の状況とご希望をお聞きします。",
  ],
  [
    "02",
    "資料を確認します",
    "所在地や登記、図面、写真など、分かる範囲から一緒に整理します。",
  ],
  [
    "03",
    "必要な確認を見極めます",
    "現地確認や専門家への相談が必要か、対応の可否を検討します。",
  ],
  [
    "04",
    "次の選択肢をご案内します",
    "管理・調査・森林整備など、必要な対応と費用を個別にお伝えします。",
  ],
];
const faqs = [
  [
    "山の正確な場所が分からなくても相談できますか？",
    "はい。分かる範囲の地名、登記資料、古い図面や写真などをもとに、最初に状況をうかがいます。",
  ],
  [
    "相続前でも相談できますか？",
    "はい。相続前の段階から、確認しておくことや今後の選択肢を整理するためのご相談を承ります。",
  ],
  [
    "必ず売却できますか？",
    "売却を前提としたサービスではありません。状況を確認したうえで、保有・管理・売却を含めた選択肢を検討します。",
  ],
  [
    "現地調査は無料ですか？",
    "無料なのは初回インタビューまでです。現地確認や調査が必要な場合は、対応可否と費用を事前にご案内します。",
  ],
];

export default function Home() {
  return (
    <main>
      <header className="site-header">
        <a
          className="brand"
          href="#top"
          aria-label={`${siteConfig.brandName} トップへ`}
        >
          <span className="brand-mark">N</span>
          <span>{siteConfig.brandName}</span>
        </a>
        <a className="header-link" href="#consultation">
          相談について
        </a>
      </header>
      <section className="hero" id="top">
        <div className="hero-landscape" aria-hidden="true">
          <span className="sun" />
          <span className="mountain mountain-back" />
          <span className="mountain mountain-front" />
          <span className="field field-one" />
          <span className="field field-two" />
        </div>
        <div className="hero-content">
          <p className="eyebrow">NATURE CAPITAL &amp; REAL ESTATE</p>
          <h1>
            自然を、
            <br />
            未来を育てる資本へ。
          </h1>
          <p className="hero-lead">
            金融資本を、ただ消費するための資金ではなく、
            <br className="desktop-only" />
            森を手入れし、地域に新しい価値を育てる力へ。
          </p>
          <div className="hero-meta">
            <span>森林・里山の相続と管理</span>
            <span>森林の計画づくりを支援</span>
          </div>
          <a className="primary-button" href="#consultation">
            二つの事業を見る <span aria-hidden="true">→</span>
          </a>
        </div>
        <p className="photo-note">掲載写真は地域の風景イメージです</p>
      </section>
      <section className="intro section-narrow">
        <p className="section-label">OUR PURPOSE</p>
        <h2>
          お金を、未来をつくる
          <br />
          資本として使う。
        </h2>
        <p>
          森は、手入れする人、時間、そして資金があって初めて、その価値を未来へつなげられます。私たちは、金融資本を、短期的に土地を評価するためだけに使うのではなく、森林・地域・そこで暮らす人の新しい価値を生み出すための資本として活かしたいと考えています。
        </p>
        <p>
          そのために、所有者の不安に寄り添う「さとやま不動産」と、現場の計画づくりを支える仕組みの両方に取り組みます。
        </p>
      </section>
      <section className="concerns section">
        <div className="section-heading">
          <p className="section-label">CONCERNS</p>
          <h2>
            こんなお悩みは
            <br />
            ありませんか。
          </h2>
        </div>
        <div className="concern-list">
          {concerns.map((concern, index) => (
            <article className="concern" key={concern}>
              <span>0{index + 1}</span>
              <p>{concern}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="consultation" id="consultation">
        <div className="consultation-copy">
          <p className="section-label">FIRST INTERVIEW</p>
          <h2>
            初回インタビューで、
            <br />
            状況を整理します。
          </h2>
          <p>
            初回のインタビューは無料です。売却を前提にせず、分かること・分からないことを一緒に確認し、次に必要な対応を考えます。
          </p>
          <p className="notice">
            現地確認、調査、専門家への相談などが必要な場合は、対応可否と費用を事前にご案内します。
          </p>
        </div>
        <ul className="check-list">
          {interviewItems.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
      <section className="flow section">
        <div className="section-heading">
          <p className="section-label">FLOW</p>
          <h2>
            ご相談から、
            <br />
            次の一歩まで。
          </h2>
        </div>
        <div className="steps">
          {steps.map(([number, title, body]) => (
            <article className="step" key={number}>
              <span>{number}</span>
              <h3>{title}</h3>
              <p>{body}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="principles">
        <p className="section-label">OUR APPROACH</p>
        <h2>
          大切にするのは、
          <br />
          土地のことと、人のこと。
        </h2>
        <div className="principle-grid">
          <p>売却ありきにしないこと</p>
          <p>権利と管理の状況から確認すること</p>
          <p>地域で実際に手入れできる人の存在を重視すること</p>
          <p>地域に仕事が残る形を目指すこと</p>
        </div>
        <p className="future">
          整った森林・里山が、地域の暮らしや将来の活動につながっていく。その可能性を、無理のない順序で考えます。
        </p>
      </section>
      <section className="faq section-narrow">
        <p className="section-label">FAQ</p>
        <h2>よくあるご質問</h2>
        <div className="faq-list">
          {faqs.map(([question, answer]) => (
            <details key={question}>
              <summary>
                {question}
                <span>+</span>
              </summary>
              <p>{answer}</p>
            </details>
          ))}
        </div>
      </section>
      <section className="cta">
        <p className="section-label">CONTACT</p>
        <h2>
          まずは、今のことを
          <br />
          お聞かせください。
        </h2>
        <p>
          ご相談窓口は現在準備中です。公開時に、電話・フォーム・受付時間をこちらにご案内します。
        </p>
        <span className="disabled-button" aria-disabled="true">
          お問い合わせ準備中
        </span>
      </section>
      <footer>
        <span>{siteConfig.brandName}</span>
        <span>© {new Date().getFullYear()} Nature Capital Real Estate</span>
      </footer>
    </main>
  );
}
