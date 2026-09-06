import "./InsightCard.css";

const TONE_MARK = {
  positive: "✓",
  warning: "!",
  neutral: "•",
};

function InsightCard({ eyebrow, title, body, tone = "neutral" }) {
  return (
    <div className={`insight-card insight-card--${tone}`}>
      <div className="insight-card-mark" aria-hidden="true">
        {TONE_MARK[tone] || TONE_MARK.neutral}
      </div>

      <div className="insight-card-body">
        <span className="insight-card-eyebrow">{eyebrow}</span>
        <h3>{title}</h3>
        <p>{body}</p>
      </div>
    </div>
  );
}

export default InsightCard;
