
import "./globals.css";

export const metadata = {
  title: "Campus Intelligence",
  description: "Unified campus dashboard with an AI assistant routed over MCP servers",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

