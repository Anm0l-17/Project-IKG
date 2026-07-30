import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'India Knowledge Graph | Event Intelligence Platform',
  description: 'AI-powered Event Intelligence & Verification Platform for Indian Affairs',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-900 antialiased">
        <header className="border-b border-slate-200 bg-white shadow-sm sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">🇮🇳</span>
              <div>
                <h1 className="font-semibold text-lg leading-none text-slate-900">
                  India Knowledge Graph
                </h1>
                <p className="text-xs text-slate-500 mt-0.5">
                  Event Intelligence & Verification Platform
                </p>
              </div>
            </div>
            <nav className="flex space-x-6 text-sm font-medium text-slate-600">
              <a href="/" className="hover:text-slate-900 transition-colors">Home</a>
              <a href="/feed" className="hover:text-slate-900 transition-colors">Feed</a>
              <a href="/graph" className="hover:text-slate-900 transition-colors">Knowledge Graph</a>
              <a href="/timeline" className="hover:text-slate-900 transition-colors">Timelines</a>
            </nav>
          </div>
        </header>
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="border-t border-slate-200 bg-white py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-xs text-slate-500">
            <p>India Knowledge Graph — Events are reality. News is evidence.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
