// insightsEngine.js
//
// Week 4 deliverable — turns raw ML outputs (Qini/uplift results,
// prescriptive optimization results, budget settings) into short,
// human-readable statements a non-technical user can act on.
//
// This module intentionally contains no fetching or React state —
// it is pure logic so it can be unit-tested and reused by any page.

const currency = (value) => {
  const num = Number(value);
  if (!Number.isFinite(num)) return "₹0";
  return `₹${num.toLocaleString("en-IN", {
    maximumFractionDigits: 0,
  })}`;
};

const percent = (value, digits = 1) => {
  const num = Number(value);
  if (!Number.isFinite(num)) return "0%";
  return `${num.toFixed(digits)}%`;
};

/**
 * Derives the best targeting fraction and best decile from Qini/uplift
 * results. Mirrors the logic already used on the Insights page so both
 * pages agree with each other.
 */
function analyzeQini(qiniData) {
  if (
    !qiniData ||
    !Array.isArray(qiniData.fractions) ||
    !Array.isArray(qiniData.qini_values) ||
    qiniData.fractions.length === 0
  ) {
    return null;
  }

  const { fractions, qini_values: qiniValues } = qiniData;

  const maxQini = Math.max(...qiniValues);
  const maxQiniIndex = qiniValues.indexOf(maxQini);
  const bestTargetingPct = fractions[maxQiniIndex] * 100;

  const upliftByDecile = qiniData.uplift_by_decile || {};
  const decileEntries = Object.entries(upliftByDecile);

  let bestDecile = null;
  if (decileEntries.length > 0) {
    bestDecile = decileEntries.reduce((best, current) =>
      Number(current[1]) > Number(best[1]) ? current : best
    );
  }

  return {
    maxQini,
    bestTargetingPct,
    bestDecile,
    hasPositiveSignal: maxQini > 0,
    hasUsableDeciles: decileEntries.length > 0,
    bestDecileUpliftPct: bestDecile ? Number(bestDecile[1]) * 100 : null,
    bestDecileNumber: bestDecile ? Number(bestDecile[0]) + 1 : null,
  };
}

/**
 * Estimates savings from targeted vs. blanket campaigns using the
 * prescription results and the budget the user configured. Blanket
 * targeting is approximated as "every customer at the configured
 * cost-per-customer" — the only baseline the app actually has data for.
 */
function estimateSavings(prescriptionData, budgetData) {
  if (!prescriptionData || !budgetData) return null;

  const totalCustomers = Number(prescriptionData.customers);
  const allocated = Number(prescriptionData.customers_allocated);
  const costPerCustomer = Number(budgetData.costPerCustomer);

  if (
    !Number.isFinite(totalCustomers) ||
    !Number.isFinite(allocated) ||
    !Number.isFinite(costPerCustomer) ||
    totalCustomers <= 0
  ) {
    return null;
  }

  const blanketCost = totalCustomers * costPerCustomer;
  const targetedCost = Number(prescriptionData.marketing_cost) || 0;
  const savings = blanketCost - targetedCost;

  return {
    savings,
    blanketCost,
    targetedCost,
    isPositive: savings > 0,
  };
}

/**
 * Main entry point. Returns an ordered array of insight card
 * descriptors: { id, eyebrow, title, body, tone }.
 * tone is one of "positive" | "neutral" | "warning" — used for styling.
 *
 * Every field degrades gracefully: missing or unusable data produces a
 * clear, non-technical explanation instead of a broken or misleading
 * number.
 */
export function generateInsights({ qiniData, prescriptionData, budgetData }) {
  const insights = [];
  const qini = analyzeQini(qiniData);

  // 1. Recommended Strategy
  if (!qini) {
    insights.push({
      id: "strategy",
      eyebrow: "Recommended strategy",
      title: "Upload results to see a recommendation",
      body: "Once causal analysis results are available, this card will recommend whether to target high-uplift customers or continue blanket targeting.",
      tone: "neutral",
    });
  } else if (!qini.hasPositiveSignal) {
    insights.push({
      id: "strategy",
      eyebrow: "Recommended strategy",
      title: "No clear high-uplift segment found",
      body: "The model isn't showing a customer group that responds meaningfully better to the campaign than random targeting. Consider reviewing the campaign design or collecting more response data before targeting narrowly.",
      tone: "warning",
    });
  } else {
    insights.push({
      id: "strategy",
      eyebrow: "Recommended strategy",
      title: "Target high-uplift customers instead of everyone",
      body: `Targeting the top ${percent(
        qini.bestTargetingPct
      )} of customers ranked by predicted uplift performs better than reaching the full customer base.`,
      tone: "positive",
    });
  }

  // 2. Estimated Savings
  const savings = estimateSavings(prescriptionData, budgetData);

  if (!prescriptionData) {
    insights.push({
      id: "savings",
      eyebrow: "Estimated savings",
      title: "Run the prescription step to see savings",
      body: "Savings compared with blanket targeting will appear here once optimization results are available.",
      tone: "neutral",
    });
  } else if (!budgetData) {
    insights.push({
      id: "savings",
      eyebrow: "Estimated savings",
      title: "Set a budget to calculate savings",
      body: "Add a cost-per-customer in Budget Settings so this card can compare targeted spend against reaching every customer.",
      tone: "neutral",
    });
  } else if (!savings) {
    insights.push({
      id: "savings",
      eyebrow: "Estimated savings",
      title: "Savings can't be calculated yet",
      body: "Some required values are missing or invalid, so a reliable savings estimate isn't available right now.",
      tone: "neutral",
    });
  } else if (!savings.isPositive) {
    insights.push({
      id: "savings",
      eyebrow: "Estimated savings",
      title: "Targeted spend is not cheaper than blanket spend",
      body: `At the current budget settings, targeting costs ${currency(
        savings.targetedCost
      )} versus ${currency(
        savings.blanketCost
      )} for reaching everyone — there's little or no cost saving here, though it may still improve revenue quality.`,
      tone: "warning",
    });
  } else {
    insights.push({
      id: "savings",
      eyebrow: "Estimated savings",
      title: `This strategy saves ${currency(savings.savings)}`,
      body: `Compared with reaching all customers at ${currency(
        savings.blanketCost
      )}, the recommended targeting spends ${currency(
        savings.targetedCost
      )} — a savings of ${currency(savings.savings)}.`,
      tone: "positive",
    });
  }

  // 3. Expected Impact (predicted revenue)
  if (!prescriptionData || !Number.isFinite(Number(prescriptionData.predicted_revenue))) {
    insights.push({
      id: "impact",
      eyebrow: "Expected impact",
      title: "Revenue impact not available yet",
      body: "Run the prescription step to estimate the additional revenue this strategy is expected to generate.",
      tone: "neutral",
    });
  } else {
    const revenue = Number(prescriptionData.predicted_revenue);
    insights.push({
      id: "impact",
      eyebrow: "Expected impact",
      title:
        revenue > 0
          ? `Expected to generate ${currency(revenue)} in revenue`
          : "Expected revenue impact is flat or negative",
      body:
        revenue > 0
          ? `The recommended strategy is projected to generate ${currency(
              revenue
            )} in additional revenue from the customers allocated a discount.`
          : `The model projects ${currency(
              revenue
            )} in revenue from this strategy — worth reviewing discount levels or targeting criteria before running the campaign.`,
      tone: revenue > 0 ? "positive" : "warning",
    });
  }

  // 4. Best Audience
  if (!qini || !qini.hasUsableDeciles) {
    insights.push({
      id: "audience",
      eyebrow: "Best audience",
      title: "Audience segment not available",
      body: "Once uplift-by-decile results are available, this card will highlight which customer segment responds best.",
      tone: "neutral",
    });
  } else if (qini.bestDecileUpliftPct <= 0) {
    insights.push({
      id: "audience",
      eyebrow: "Best audience",
      title: "No segment shows positive uplift",
      body: "Every customer segment currently shows flat or negative estimated uplift. Targeting narrowly may not help until the model or campaign is revisited.",
      tone: "warning",
    });
  } else {
    insights.push({
      id: "audience",
      eyebrow: "Best audience",
      title: `Focus on decile ${qini.bestDecileNumber}`,
      body: `Customers in decile ${qini.bestDecileNumber} show the strongest estimated uplift, at approximately ${percent(
        qini.bestDecileUpliftPct,
        2
      )}. Prioritize this group if targeting is limited.`,
      tone: "positive",
    });
  }

  return insights;
}
