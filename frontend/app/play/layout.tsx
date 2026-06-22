import { SoundToggle } from "@/components/shared/SoundToggle";

export default function PlayLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <main className="bg-app-gradient min-h-screen">
      <div className="absolute right-3 top-3">
        <SoundToggle />
      </div>
      <div className="mx-auto flex min-h-screen max-w-lg flex-col justify-center px-6 py-10">
        {children}
      </div>
    </main>
  );
}
