const currency = (value) => {

  const num = Number(value);

  if (!Number.isFinite(num)) {
    return "₹0";
  }

  return `₹${num.toLocaleString(
    "en-IN",
    {
      maximumFractionDigits: 0
    }
  )}`;

};


const percent = (
  value,
  digits = 1
) => {

  const num =
    Number(value);

  if (
    !Number.isFinite(num)
  ) {

    return "0%";

  }

  return `${num.toFixed(
    digits
  )}%`;

};


function analyzeQini(
  qiniData
) {

  if (
    !qiniData
    ||
    !Array.isArray(
      qiniData.fractions
    )
    ||
    !Array.isArray(
      qiniData.qini_values
    )
    ||
    !qiniData.fractions.length
  ) {

    return null;

  }


  const maxQini =
    Math.max(
      ...qiniData.qini_values
    );


  const index =
    qiniData.qini_values.indexOf(
      maxQini
    );


  const bestTargetingPct =
    Number(
      qiniData.fractions[index]
    ) * 100;


  const entries =
    Object.entries(
      qiniData.uplift_by_decile
      || {}
    );


  const bestDecile =
    entries.length

      ? entries.reduce(
          (
            best,
            current
          ) =>
            Number(
              current[1]
            )
            >
            Number(
              best[1]
            )
              ? current
              : best
        )

      : null;


  return {

    maxQini,

    bestTargetingPct,

    bestDecile,

    hasPositiveSignal:
      maxQini > 0,

    bestDecileUpliftPct:
      bestDecile
        ? Number(
            bestDecile[1]
          ) * 100
        : null,

    bestDecileNumber:
      bestDecile
        ? Number(
            bestDecile[0]
          ) + 1
        : null

  };

}


export function generateInsights({
  qiniData,
  prescriptionData,
  budgetData
}) {

  const insights = [];

  const qini =
    analyzeQini(
      qiniData
    );


  if (!qini) {

    insights.push({

      id:
        "strategy",

      eyebrow:
        "Recommended strategy",

      title:
        "Upload data to generate a recommendation",

      body:
        "The dashboard will calculate customer-level causal effects and Qini results after the dataset is uploaded.",

      tone:
        "neutral"

    });

  } else if (
    !qini.hasPositiveSignal
  ) {

    insights.push({

      id:
        "strategy",

      eyebrow:
        "Recommended strategy",

      title:
        "No positive Qini signal in the current analysis",

      body:
        "The current ranking does not show a positive cumulative uplift advantage. Review the campaign data before narrowing the target audience.",

      tone:
        "warning"

    });

  } else {

    insights.push({

      id:
        "strategy",

      eyebrow:
        "Recommended strategy",

      title:
        "Prioritize higher-uplift customers",

      body:
        `The current Qini curve reaches its maximum at approximately ${percent(
          qini.bestTargetingPct
        )} targeted customers.`,

      tone:
        "positive"

    });

  }


  if (
    !prescriptionData
    ||
    !budgetData
  ) {

    insights.push({

      id:
        "budget",

      eyebrow:
        "Budget status",

      title:
        "Run optimization to see budget usage",

      body:
        "Set a campaign budget and rerun the optimizer to calculate the current spend and remaining budget.",

      tone:
        "neutral"

    });

  } else {

    const budget =
      Number(
        budgetData.total_budget
      );

    const cost =
      Number(
        prescriptionData.marketing_cost
      );

    const remaining =
      budget - cost;

    const utilization =
      budget > 0
        ? (
            cost / budget
          ) * 100
        : 0;


    insights.push({

      id:
        "budget",

      eyebrow:
        "Budget status",

      title:
        `${currency(
          Math.max(
            0,
            remaining
          )
        )} remaining`,

      body:
        `The optimizer uses ${percent(
          utilization,
          1
        )} of the configured ${currency(
          budget
        )} budget while respecting the cost constraint.`,

      tone:
        remaining >= 0
          ? "positive"
          : "warning"

    });

  }


  if (
    !prescriptionData
    ||
    !Number.isFinite(
      Number(
        prescriptionData
          .predicted_revenue
      )
    )
  ) {

    insights.push({

      id:
        "impact",

      eyebrow:
        "Predicted revenue",

      title:
        "Optimization output not available",

      body:
        "Run the optimizer after setting the budget to generate the current predicted-revenue total.",

      tone:
        "neutral"

    });

  } else {

    const revenue =
      Number(
        prescriptionData
          .predicted_revenue
      );


    insights.push({

      id:
        "impact",

      eyebrow:
        "Predicted revenue",

      title:
        currency(
          revenue
        ),

      body:
        "This is the total predicted revenue associated with the selected discount assignments in the prepared optimization matrix. It is not labeled as incremental revenue without a separate baseline calculation.",

      tone:
        "positive"

    });

  }


  if (
    !qini
    ||
    !qini.bestDecile
  ) {

    insights.push({

      id:
        "audience",

      eyebrow:
        "Best audience",

      title:
        "Audience segment not available",

      body:
        "Decile-level uplift will appear after live causal analysis is completed.",

      tone:
        "neutral"

    });

  } else {

    const uplift =
      qini.bestDecileUpliftPct;


    insights.push({

      id:
        "audience",

      eyebrow:
        "Best audience",

      title:
        uplift > 0
          ? `Focus on decile ${qini.bestDecileNumber}`
          : "No positive-uplift decile",

      body:
        uplift > 0

          ? `Decile ${qini.bestDecileNumber} has the strongest estimated uplift at approximately ${percent(
              uplift,
              2
            )}.`

          : "The strongest decile is not showing positive estimated uplift in the current upload.",

      tone:
        uplift > 0
          ? "positive"
          : "warning"

    });

  }


  return insights;

}