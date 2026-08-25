import {
  BrowserRouter,
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import Navbar from "./components/Navbar";
import UploadData from "./components/UploadData";
import BudgetSettings from "./components/BudgetSettings";
import Insights from "./components/Insights";
import Dashboard from "./components/Dashboard";
import AllocationMatrix from "./components/AllocationMatrix";

import "./App.css";

function App() {
  return (
    <BrowserRouter>

      <Navbar />

      <main>

        <Routes>

          <Route
            path="/"
            element={<Dashboard />}
          />

          <Route
            path="/upload"
            element={<UploadData />}
          />

          <Route
            path="/budget"
            element={<BudgetSettings />}
          />

          <Route
            path="/insights"
            element={<Insights />}
          />

          <Route
            path="/prescription"
            element={<AllocationMatrix />}
          />

          <Route
            path="*"
            element={<Navigate to="/" replace />}
          />

        </Routes>

      </main>

    </BrowserRouter>
  );
}

export default App;