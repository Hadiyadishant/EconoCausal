import { NavLink } from "react-router-dom";
import "./Navbar.css";


export default function Navbar() {

  return (

    <header className="navbar">

      {/* Brand */}

      <NavLink
        to="/"
        className="navbar-brand"
      >

        <span className="brand-mark">
          EC
        </span>

        <span>

          <strong>
            EconoCausal
          </strong>

          <small>
            Causal AI Platform
          </small>

        </span>

      </NavLink>


      {/* Navigation */}

      <nav className="nav-links">

        <NavLink
          to="/"
          end
        >
          Dashboard
        </NavLink>


        <NavLink
          to="/upload"
        >
          Upload Data
        </NavLink>


        <NavLink
          to="/budget"
        >
          Budget Settings
        </NavLink>


        <NavLink
          to="/insights"
        >
          Insights
        </NavLink>

      </nav>

    </header>
  );

}
