import Link from "next/link";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <main className="bg-app-gradient min-h-screen">
      <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6 py-10">
        <Link
          href="/"
          className="mb-6 text-center font-display text-2xl font-extrabold text-primary"
        >
          DarsPro
        </Link>
        {children}
      </div>
    </main>
  );
}
