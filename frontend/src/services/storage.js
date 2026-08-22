const DATASET_KEY =
  "econocausal_dataset";

const BUDGET_KEY =
  "econocausal_budget";


export const saveDataset = (dataset) => {
  localStorage.setItem(
    DATASET_KEY,
    JSON.stringify(dataset)
  );
};


export const getDataset = () => {
  const data =
    localStorage.getItem(DATASET_KEY);

  if (!data) {
    return null;
  }

  try {
    return JSON.parse(data);
  } catch (error) {
    console.error(
      "Unable to read saved dataset:",
      error
    );

    return null;
  }
};


export const saveBudget = (budget) => {
  localStorage.setItem(
    BUDGET_KEY,
    JSON.stringify(budget)
  );
};


export const getBudget = () => {
  const data =
    localStorage.getItem(BUDGET_KEY);

  if (!data) {
    return null;
  }

  try {
    return JSON.parse(data);
  } catch (error) {
    console.error(
      "Unable to read saved budget:",
      error
    );

    return null;
  }
};


export const clearStorage = () => {
  localStorage.removeItem(DATASET_KEY);
  localStorage.removeItem(BUDGET_KEY);
};