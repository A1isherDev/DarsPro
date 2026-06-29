"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { ArrowLeft, LayoutDashboard, ShieldCheck, Users } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/store";

const NAV = [
  { href: "/admin/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/admin", label: "Review navbati", icon: ShieldCheck },
  { href: "/admin/users", label: "Foydalanuvchilar", icon: Users },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, initialized, loadMe } = useAuth();

  useEffect(() => {
    if (!initialized) loadMe();
  }, [initialized, loadMe]);

  useEffect(() => {
    if (initialized && !user) router.replace("/login");
    else if (initialized && user && !user.is_staff) router.replace("/dashboard");
  }, [initialized, user, router]);

  if (!initialized || !user || !user.is_staff) {
    return (
      <div className="flex min-h-screen items-center justify-center text-muted-foreground">
        Tekshirilmoqda…
      </div>
    );
  }

  return (
    <div className="flex min-h-screen">
      <aside className="flex w-60 flex-col border-r border-border bg-card p-4">
        <div className="mb-6 px-2">
          <p className="text-xl font-bold">DarsPro</p>
          <p className="text-xs text-muted-foreground">Admin panel</p>
        </div>
        <nav className="flex flex-1 flex-col gap-1">
          {NAV.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                pathname === href
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted"
              )}
            >
              <Icon size={18} />
              {label}
            </Link>
          ))}
        </nav>
        <Link href="/dashboard">
          <Button variant="ghost" size="sm" className="w-full justify-start">
            <ArrowLeft size={16} /> Dashboardga
          </Button>
        </Link>
      </aside>
      <main className="flex-1 overflow-y-auto p-8">{children}</main>
    </div>
  );
}
