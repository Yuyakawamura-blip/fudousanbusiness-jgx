import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "森林・里山の相続と管理のご相談 | ネイチャーキャピタル・リアルエステイト", description: "北海道・東北・山梨・四国の森林・里山について、相続・管理・境界に関する初回インタビューを無料で承ります。" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="ja"><body>{children}</body></html>; }
