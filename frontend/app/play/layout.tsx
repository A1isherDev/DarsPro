export default function PlayLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <main className="bg-app-gradient min-h-screen">
      <div className="mx-auto flex min-h-screen max-w-lg flex-col justify-center px-6 py-10">
        {children}
      </div>
    </main>
  );
}
