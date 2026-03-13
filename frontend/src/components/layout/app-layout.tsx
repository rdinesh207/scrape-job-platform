import { Briefcase, LogOut, Search, Sparkles, UserCircle2 } from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { Button } from "../ui/button";
import { useAuth } from "../../state/auth-context";

const links = [
  { to: "/dashboard", label: "Dashboard", icon: Sparkles },
  { to: "/profile", label: "Profile", icon: UserCircle2 },
  { to: "/search", label: "Search Jobs", icon: Search },
];

export function AppLayout() {
  const { signOut, user } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b border-slate-800 bg-slate-950/70 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-brand/20 p-2">
              <Briefcase className="h-5 w-5 text-indigo-300" />
            </div>
            <div>
              <p className="font-semibold">CareerMatch Platform</p>
              <p className="text-xs text-slate-400">AI job matching workspace</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="hidden text-sm text-slate-400 md:inline">{user?.email}</span>
            <Button
              variant="secondary"
              size="sm"
              onClick={async () => {
                await signOut();
                navigate("/auth");
              }}
            >
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>
      </header>
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-6 py-6 md:grid-cols-[220px_1fr]">
        <aside className="rounded-xl border border-slate-800 bg-card/60 p-3">
          <nav className="space-y-2">
            {links.map((link) => {
              const Icon = link.icon;
              return (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={({ isActive }) =>
                    `flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition ${
                      isActive ? "bg-brand text-white" : "text-slate-300 hover:bg-slate-800"
                    }`
                  }
                >
                  <Icon className="h-4 w-4" />
                  {link.label}
                </NavLink>
              );
            })}
          </nav>
        </aside>
        <main>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
