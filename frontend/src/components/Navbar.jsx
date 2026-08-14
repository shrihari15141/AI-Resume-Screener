import {
  BarChart3,
  Bell,
  BriefcaseBusiness,
  BrainCircuit,
  LayoutDashboard,
  Menu,
  Star,
  User,
  Users,
  X
} from "lucide-react";
import { useState } from "react";
import { NavLink } from "react-router-dom";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/jobs", label: "Jobs", icon: BriefcaseBusiness },
  { to: "/candidates", label: "Candidates", icon: Users },
  { to: "/screening", label: "AI Screening", icon: BrainCircuit },
  { to: "/reports", label: "Reports", icon: BarChart3 },
  { to: "/shortlisted", label: "Shortlisted", icon: Star }
];

function NavItem({ item, mobile = false, onClick }) {
  const Icon = item.icon;
  return (
    <NavLink
      to={item.to}
      onClick={onClick}
      className={({ isActive }) =>
        `${mobile ? "mobile-nav-link" : "nav-link"} ${isActive ? "nav-link-active" : "nav-link-idle"}`
      }
    >
      <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
      <span className="truncate">{item.label}</span>
    </NavLink>
  );
}

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="app-header">
      <div className="app-nav-shell">
        <NavLink to="/dashboard" className="brand-link">
          <span className="brand-icon">
            <BrainCircuit className="h-5 w-5" aria-hidden="true" />
          </span>
          ResumeAI
        </NavLink>
        <nav className="hidden items-center gap-1 rounded-lg bg-surface/70 p-1 lg:flex" aria-label="Primary navigation">
          {navItems.map((item) => (
            <NavItem key={item.to} item={item} />
          ))}
        </nav>
        <div className="hidden items-center gap-2 lg:flex">
          <button className="icon-button" aria-label="Notifications" title="Notifications">
            <Bell className="h-4 w-4" aria-hidden="true" />
          </button>
          <NavLink to="/profile" className="workspace-link">
            <User className="h-4 w-4" aria-hidden="true" />
            Workspace
          </NavLink>
        </div>
        <button
          className="icon-button lg:hidden"
          onClick={() => setOpen(true)}
          aria-label="Open menu"
          aria-expanded={open}
        >
          <Menu className="h-5 w-5" aria-hidden="true" />
        </button>
      </div>

      {open && (
        <div className="mobile-menu-backdrop" onClick={() => setOpen(false)}>
          <div className="mobile-menu-panel" onClick={(event) => event.stopPropagation()}>
            <div className="mobile-menu-header">
              <span className="brand-link">
                <span className="brand-icon">
                  <BrainCircuit className="h-5 w-5" aria-hidden="true" />
                </span>
                ResumeAI
              </span>
              <button className="icon-button h-9 w-9" onClick={() => setOpen(false)} aria-label="Close menu">
                <X className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
            <nav className="grid gap-1" aria-label="Mobile navigation">
              {navItems.map((item) => (
                <NavItem key={item.to} item={item} mobile onClick={() => setOpen(false)} />
              ))}
              <NavLink
                to="/profile"
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  `mobile-nav-link ${isActive ? "nav-link-active" : "nav-link-idle"}`
                }
              >
                <User className="h-4 w-4 shrink-0" aria-hidden="true" />
                <span className="truncate">Workspace</span>
              </NavLink>
            </nav>
          </div>
        </div>
      )}
    </header>
  );
}
