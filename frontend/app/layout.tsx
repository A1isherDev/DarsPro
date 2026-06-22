import type { Metadata } from "next";
import { Baloo_2, Nunito } from "next/font/google";

import { ToastProvider } from "@/components/ui/toast";
import "./globals.css";

const nunito = Nunito({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const baloo = Baloo_2({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["500", "600", "700", "800"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "DarsPro — O'qituvchilar uchun o'yin platformasi",
  description:
    "O'zbekiston maktab o'qituvchilari uchun tayyor o'yinlar va kontent kutubxonasi.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="uz" className={`${nunito.variable} ${baloo.variable}`}>
      <body>
        <ToastProvider>{children}</ToastProvider>
      </body>
    </html>
  );
}
