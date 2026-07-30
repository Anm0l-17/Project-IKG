export default function HomePage() {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <section className="bg-white border border-slate-200 rounded-xl p-8 shadow-sm space-y-4">
        <div className="inline-flex items-center space-x-2 px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full text-xs font-medium border border-emerald-200">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>System Status: Planning & Core Initialization</span>
        </div>
        <h2 className="text-3xl font-bold text-slate-900 tracking-tight">
          Transforming Fragmented News into Verified Knowledge
        </h2>
        <p className="text-slate-600 max-w-3xl leading-relaxed">
          India Knowledge Graph connects daily Indian news articles into evolving real-world events, multi-source verification timelines, and interactive knowledge graphs.
        </p>
      </section>

      {/* Metric Highlights */}
      <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 p-5 rounded-lg shadow-sm">
          <div className="text-sm font-medium text-slate-500">Discovery Engine</div>
          <div className="text-xl font-semibold text-slate-900 mt-1">GKToday RSS</div>
          <div className="text-xs text-slate-400 mt-1">Primary discovery source</div>
        </div>

        <div className="bg-white border border-slate-200 p-5 rounded-lg shadow-sm">
          <div className="text-sm font-medium text-slate-500">Verification Consensus</div>
          <div className="text-xl font-semibold text-slate-900 mt-1">The Hindu & TOI</div>
          <div className="text-xs text-slate-400 mt-1">2/3 majority vote rule</div>
        </div>

        <div className="bg-white border border-slate-200 p-5 rounded-lg shadow-sm">
          <div className="text-sm font-medium text-slate-500">Graph Engine</div>
          <div className="text-xl font-semibold text-slate-900 mt-1">React Force Graph</div>
          <div className="text-xs text-slate-400 mt-1">Interactive network traversal</div>
        </div>

        <div className="bg-white border border-slate-200 p-5 rounded-lg shadow-sm">
          <div className="text-sm font-medium text-slate-500">Hybrid AI</div>
          <div className="text-xl font-semibold text-slate-900 mt-1">Gemini + Qwen3:8B</div>
          <div className="text-xs text-slate-400 mt-1">Deterministic first reasoning</div>
        </div>
      </section>
    </div>
  );
}
