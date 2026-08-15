import { useState } from "react";
import "./BudgetSettings.css";

export default function BudgetSettings() {
  const [budget, setBudget] = useState(5000);
  const [maxDiscount, setMaxDiscount] = useState(30);
  const [saved, setSaved] = useState(false);

  const handleSubmit = (event) => {
    event.preventDefault();
    setSaved(true);
  };

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <span className="eyebrow">CAMPAIGN CONFIGURATION</span>
          <h1>Budget Settings</h1>
          <p>Define campaign constraints before treatment allocation.</p>
        </div>
      </div>

      <div className="settings-card">
        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="budget">Campaign Budget</label>
            <div className="input-group">
              <span>$</span>
              <input
                id="budget"
                type="number"
                min="0"
                step="100"
                value={budget}
                onChange={(e) => {
                  setBudget(e.target.value);
                  setSaved(false);
                }}
              />
            </div>
            <small>Maximum amount available for the campaign.</small>
          </div>

          <div className="field">
            <label htmlFor="discount">Maximum Discount</label>
            <div className="input-group">
              <input
                id="discount"
                type="number"
                min="0"
                max="30"
                step="5"
                value={maxDiscount}
                onChange={(e) => {
                  setMaxDiscount(e.target.value);
                  setSaved(false);
                }}
              />
              <span>%</span>
            </div>
            <small>Maximum discount allowed per customer.</small>
          </div>

          <div className="settings-summary">
            <div>
              <span>Campaign budget</span>
              <strong>${Number(budget || 0).toLocaleString()}</strong>
            </div>
            <div>
              <span>Maximum discount</span>
              <strong>{maxDiscount}%</strong>
            </div>
          </div>

          <button className="save-button" type="submit">
            Save Settings
          </button>

          {saved && <p className="saved-message">✓ Settings saved successfully.</p>}
        </form>
      </div>
    </section>
  );
}
