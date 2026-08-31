import { useEffect, useMemo, useState } from "react";
import "./Prescription.css";

function Prescription() {
  const [data, setData] = useState(null);
  const [search, setSearch] = useState("");
  const [discountFilter, setDiscountFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/data/optimization_results.json?v=1")
      .then((res) => {
        if (!res.ok) {
          throw new Error("Unable to load optimization results");
        }
        return res.json();
      })
      .then((result) => {
        if (!result.allocations || !Array.isArray(result.allocations)) {
          throw new Error("Invalid optimization result format");
        }

        setData(result);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const allocations = data?.allocations || [];

  const filteredData = useMemo(() => {
    return allocations.filter((row) => {
      const matchesSearch = String(row.customer_id)
        .toLowerCase()
        .includes(search.toLowerCase());

      const matchesDiscount =
        discountFilter === "all" ||
        Number(row.optimal_discount) === Number(discountFilter);

      return matchesSearch && matchesDiscount;
    });
  }, [allocations, search, discountFilter]);

  if (loading) {
    return (
      <div className="prescription-page">
        <h1>Loading Prescription...</h1>
      </div>
    );
  }

  if (error) {
    return (
      <div className="prescription-page">
        <h1>Unable to load results</h1>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="prescription-page">

      <div className="page-header">
        <span>PRESCRIPTIVE OPTIMIZATION</span>

        <h1>Final Prescription</h1>

        <p>
          Customer-level optimal discount allocation generated
          by the prescriptive optimization model.
        </p>
      </div>

      <div className="summary-grid">

        <div className="summary-card">
          <span>Total Customers</span>
          <strong>
            {Number(data.customers).toLocaleString()}
          </strong>
        </div>

        <div className="summary-card">
          <span>Customers Allocated</span>
          <strong>
            {Number(data.customers_allocated).toLocaleString()}
          </strong>
        </div>

        <div className="summary-card">
          <span>Predicted Revenue</span>
          <strong>
            ₹{Number(data.predicted_revenue).toFixed(2)}
          </strong>
        </div>

        <div className="summary-card">
          <span>Marketing Cost</span>
          <strong>
            ₹{Number(data.marketing_cost).toFixed(2)}
          </strong>
        </div>

      </div>

      <div className="budget-status">
        <strong>Budget:</strong>{" "}
        ₹{Number(data.budget).toFixed(2)}

        {" | "}

        <strong>Remaining:</strong>{" "}
        ₹{Number(data.budget_remaining).toFixed(2)}

        <span className="success">
          {" "}✓ Budget satisfied
        </span>
      </div>

      <div className="filters">

        <div>
          <label>Search Customer</label>

          <input
            type="text"
            placeholder="Enter customer ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div>
          <label>Optimal Discount</label>

          <select
            value={discountFilter}
            onChange={(e) =>
              setDiscountFilter(e.target.value)
            }
          >
            <option value="all">All Discounts</option>
            <option value="0">0%</option>
            <option value="5">5%</option>
            <option value="10">10%</option>
            <option value="15">15%</option>
            <option value="20">20%</option>
            <option value="25">25%</option>
            <option value="30">30%</option>
          </select>
        </div>

      </div>

      <div className="allocation-card">

        <div className="allocation-header">
          <h2>Allocation Matrix</h2>

          <p>
            {filteredData.length.toLocaleString()}
            {" "}customers displayed
          </p>
        </div>

        <div className="table-container">

          <table>

            <thead>
              <tr>
                <th>Customer ID</th>
                <th>Optimal Discount</th>
                <th>Predicted Revenue</th>
                <th>Marketing Cost</th>
              </tr>
            </thead>

            <tbody>

              {filteredData.map((row) => (
                <tr key={row.customer_id}>

                  <td>
                    {row.customer_id}
                  </td>

                  <td>
                    <span
                      className={
                        Number(row.optimal_discount) > 0
                          ? "discount active"
                          : "discount"
                      }
                    >
                      {Number(row.optimal_discount).toFixed(0)}%
                    </span>
                  </td>

                  <td>
                    ₹{Number(row.predicted_revenue).toFixed(2)}
                  </td>

                  <td>
                    ₹{Number(row.marketing_cost).toFixed(2)}
                  </td>

                </tr>
              ))}

            </tbody>

          </table>

        </div>

      </div>

    </div>
  );
}

export default Prescription;