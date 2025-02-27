import "~/styles/globals.css";

import ReactQueryProvider from "./utils/ReactQueryProvider";
import { GeistSans } from "geist/font/sans";
import { type Metadata } from "next";

export const metadata: Metadata = {
  title: "Minecraft Manager Console",
  description: "A Minecraft server manager console for servers hosted on AWS",
  icons: [{ rel: "icon", url: "/favicon.ico" }],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <ReactQueryProvider>
      <html lang="en" className={`${GeistSans.variable}`}>
        <body suppressHydrationWarning={true}>{children}</body>
      </html>
    </ReactQueryProvider>
  );
}
