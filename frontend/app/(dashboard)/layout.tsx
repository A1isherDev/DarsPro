"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  BookOpen,
  FolderOpen,
  LayoutDashboard,
  LogOut,
  Menu,
  Plus,
  Radio,
  ShieldCheck,
  X,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/card";
import { PLAN_LABELS, cn } from "@/lib/utils";
import { useAuth } from "@/lib/store";

const NAV = [
  { href: "/dashboard", label: "Boshqaruv", icon: LayoutDashboard },
  { href: "/library", label: "Kutubxona", icon: BookOpen },
  { href: "/builder", label: "Yaratish", icon: Plus },
  { href: "/my-content", label: "Mening kontentim", icon: FolderOpen },
  { href: "/sessions", label: "Sessiyalar", icon: Radio },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, initialized, loadMe, logout } = useAuth();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!initialized) loadMe();
  }, [initialized, loadMe]);

  useEffect(() => {
    if (initialized && !user) router.replace("/login");
  }, [initialized, user, router]);

  // Marshrut o'zgarsa mobil drawer yopiladi
  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  if (!initialized || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center text-muted-foreground">
        Yuklanmoqda…
      </div>
    );
  }

  const isActive = (href: string) =>
    pathname === href || pathname.startsWith(href + "/");

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      {/* Mobil yuqori panel */}
      <header className="flex items-center justify-between border-b border-border bg-card p-3 md:hidden">
        <Link href="/dashboard" className="px-1 text-lg font-bold">
          DarsPro
        </Link>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setOpen((o) => !o)}
          aria-label="Menyu"
        >
          {open ? <X size={20} /> : <Menu size={20} />}
        </Button>
      </header>

      {/* Mobil drawer fon qoplamasi */}
      {open && (
        <div
          className="fixed inset-0 z-30 bg-black/40 md:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 flex w-60 flex-col border-r border-border bg-card p-4 transition-transform md:static md:z-auto md:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <Link
          href="/dashboard"
          className="mb-6 hidden px-2 text-xl font-bold md:block"
        >
          DarsPro
        </Link>
        <nav className="flex flex-1 flex-col gap-1">
          {NAV.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive(href)
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted"
              )}
            >
              <Icon size={18} />
              {label}
            </Link>
          ))}
          {user.is_staff && (
            <Link
              href="/admin"
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive("/admin")
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted"
              )}
            >
              <ShieldCheck size={18} />
              Admin panel
            </Link>
          )}
        </nav>
        <div className="mt-4 border-t border-border pt-4">
          <Link
            href="/profile"
            className="flex items-center justify-between rounded-md px-1 py-1 hover:bg-muted"
          >
            <div className="min-w-0">
              <p className="truncate text-sm font-medium">
                {user.full_name || user.email}
              </p>
              <Badge>{PLAN_LABELS[user.effective_plan]}</Badge>
            </div>
          </Link>
          <Button
            variant="ghost"
            size="sm"
            className="mt-3 w-full justify-start"
            onClick={async () => {
              await logout();
              router.replace("/login");
            }}
          >
            <LogOut size={16} /> Chiqish
          </Button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto p-5 md:p-8">{children}</main>
    </div>
  );
}
