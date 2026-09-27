'use client';

import React, { useState, useEffect, useTransition } from 'react';
import Link from 'next/link';
import { searchEvents } from '@/lib/api';
import { SearchResultItem, SearchResponse } from '@/lib/types';
import {
  Search,
  Sparkles,
  ShieldCheck,
  Clock,
  Layers,
  SlidersHorizontal,
  ChevronRight,
  AlertCircle,
  HelpCircle,
  Hash,
} from 'lucide-react';

const CATEGORIES = [
  'All',
  'Parliament',
  'Economics',
  'Trade',
  'Defence',
  'Geopolitics',
  'Current Affairs',
];

const MODES: { id: 'hybrid' | 'semantic' | 'lexical'; label: string; desc: string }[] = [
  { id: 'hybrid', label: 'Hybrid Search', desc: 'Combines keyword hits + dense vector semantics' },
  { id: 'semantic', label: 'Semantic (pgvector)', desc: 'Meaning-based 384-dim conceptual similarity' },
  { id: 'lexical', label: 'Exact Keyword', desc: 'Exact token & title match' },
];

const VERIFICATION_FILTERS = ['All', 'VERIFIED', 'DEVELOPING'];

function MatchTypeBadge({ type, score }: { type: string; score: number }) {
  const percentage = Math.round(score * 100);
  if (type === 'HYBRID') {
    return (
      <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
        <Sparkles className="w-3 h-3 text-indigo-500" />
        <span>HYBRID ({percentage}%)</span>
      </span>
    );
  }
  if (type === 'SEMANTIC') {
    return (
      <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-50 text-purple-700 border border-purple-200">
        <Sparkles className="w-3 h-3 text-purple-500" />
        <span>SEMANTIC ({percentage}%)</span>
      </span>
    );
  }
  if (type === 'LEXICAL') {
    return (
      <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-cyan-50 text-cyan-700 border border-cyan-200">
        <Hash className="w-3 h-3 text-cyan-500" />
        <span>EXACT ({percentage}%)</span>
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-600 border border-slate-200">
      RELEVANCE ({percentage}%)
    </span>
  );
}

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [activeQuery, setActiveQuery] = useState('');
  const [mode, setMode] = useState<'hybrid' | 'semantic' | 'lexical'>('hybrid');
  const [category, setCategory] = useState('All');
  const [verificationFilter, setVerificationFilter] = useState('All');

  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [totalResults, setTotalResults] = useState(0);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const performSearch = async (searchTerm: string) => {
    if (!searchTerm.trim()) return;
    setLoading(true);
    setError(null);
    setHasSearched(true);
    setActiveQuery(searchTerm);

    try {
      const resp = await searchEvents(searchTerm.trim(), {
        mode,
        category: category === 'All' ? undefined : category,
        verificationStatus: verificationFilter === 'All' ? undefined : verificationFilter,
        limit: 30,
      });
      setResults(resp.results);
      setTotalResults(resp.total_results);
    } catch (err: any) {
      setError(err.message || 'Search failed. Please try again.');
      setResults([]);
      setTotalResults(0);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    performSearch(query);
  };

  // Trigger search on filter changes if there's an active query
  useEffect(() => {
    if (activeQuery) {
      performSearch(activeQuery);
    }
  }, [mode, category, verificationFilter]);

  const formattedDate = (iso: string) =>
    new Date(iso).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Search Header */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-sm space-y-5">
        <div className="space-y-1.5">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-semibold border border-indigo-200">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Hybrid & Vector Search</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Event Intelligence Search
          </h1>
          <p className="text-sm text-slate-500 max-w-2xl leading-relaxed">
            Search across India Knowledge Graph events using high-dimensional pgvector semantic
            embeddings and keyword matching with Reciprocal Rank scoring.
          </p>
        </div>

        {/* Search Input Box */}
        <form onSubmit={handleSearchSubmit} className="relative flex items-center">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search Indian affairs (e.g., 'defence submarine nuclear', 'GST cancer medicines', 'FTA talks')..."
              className="w-full pl-12 pr-4 py-3.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 shadow-inner"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="ml-3 px-6 py-3.5 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 text-white rounded-xl text-sm font-semibold transition-colors shadow-sm flex items-center space-x-2"
          >
            <span>Search</span>
            {loading && <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />}
          </button>
        </form>

        {/* Mode Selector */}
        <div className="pt-2 border-t border-slate-100 flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-slate-500 mr-2 flex items-center space-x-1">
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Mode:</span>
          </span>
          {MODES.map((m) => (
            <button
              key={m.id}
              type="button"
              onClick={() => setMode(m.id)}
              className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${
                mode === m.id
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
              title={m.desc}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {/* Filters Bar */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex flex-wrap items-center justify-between gap-4">
        {/* Category Pills */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-xs font-semibold text-slate-400 mr-1">Category:</span>
          {CATEGORIES.map((c) => (
            <button
              key={c}
              onClick={() => setCategory(c)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
                category === c
                  ? 'bg-slate-900 text-white'
                  : 'bg-slate-50 text-slate-600 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              {c}
            </button>
          ))}
        </div>

        {/* Verification Status Pills */}
        <div className="flex items-center space-x-1.5">
          <span className="text-xs font-semibold text-slate-400 mr-1">Status:</span>
          {VERIFICATION_FILTERS.map((vf) => (
            <button
              key={vf}
              onClick={() => setVerificationFilter(vf)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
                verificationFilter === vf
                  ? 'bg-slate-900 text-white'
                  : 'bg-slate-50 text-slate-600 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              {vf}
            </button>
          ))}
        </div>
      </div>

      {/* Results Header */}
      {hasSearched && !loading && (
        <div className="flex items-center justify-between px-1">
          <p className="text-xs font-semibold text-slate-500">
            Found <span className="text-slate-900 font-bold">{totalResults}</span> results for &ldquo;{activeQuery}&rdquo; in {mode} mode
          </p>
        </div>
      )}

      {/* Results List */}
      {loading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-white border border-slate-200 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-red-500 mx-auto" />
          <p className="text-sm font-semibold text-red-800">{error}</p>
        </div>
      ) : hasSearched && results.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-xl p-16 text-center space-y-3">
          <HelpCircle className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-slate-800">No events matched your query</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Try switching to <strong>Semantic (pgvector)</strong> mode for conceptual matches, or broaden your category and verification filters.
          </p>
        </div>
      ) : results.length > 0 ? (
        <div className="space-y-3">
          {results.map((res) => (
            <div
              key={res.id}
              className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md hover:border-slate-300 transition-all space-y-3"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 space-y-2 min-w-0">
                  {/* Badges */}
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                      {res.category}
                    </span>
                    <MatchTypeBadge type={res.match_type} score={res.relevance_score} />
                    {res.verification_status === 'VERIFIED' ? (
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        <ShieldCheck className="w-3 h-3" />
                        <span>VERIFIED</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-sky-50 text-sky-700 border border-sky-200">
                        <Clock className="w-3 h-3" />
                        <span>DEVELOPING</span>
                      </span>
                    )}
                    {res.grouping_status === 'GROUPED' && res.primary_story_id && (
                      <Link
                        href={`/stories/${res.primary_story_id}`}
                        className="inline-flex items-center space-x-1 text-[10px] font-semibold text-indigo-600 hover:text-indigo-800"
                      >
                        <Layers className="w-3 h-3" />
                        <span>In Story</span>
                      </Link>
                    )}
                  </div>

                  {/* Title */}
                  <h3 className="text-base font-bold text-slate-900 leading-snug hover:text-indigo-600 transition-colors">
                    <Link href={`/events/${res.id}`}>{res.title}</Link>
                  </h3>

                  {/* Snippet / Summary */}
                  {res.highlight_snippet ? (
                    <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                      &ldquo;{res.highlight_snippet}&rdquo;
                    </p>
                  ) : res.summary ? (
                    <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">{res.summary}</p>
                  ) : null}
                </div>

                {/* Score meters */}
                <div className="flex-shrink-0 text-right space-y-1.5 min-w-[110px]">
                  <div className="text-xs font-bold text-slate-900">
                    {Math.round(res.relevance_score * 100)}% <span className="text-[10px] font-normal text-slate-400">Match</span>
                  </div>
                  <div className="text-[10px] text-slate-400 space-y-0.5">
                    <div>Lex: {Math.round(res.lexical_score * 100)}%</div>
                    <div>Sem: {Math.round(res.semantic_score * 100)}%</div>
                  </div>
                  <Link
                    href={`/events/${res.id}`}
                    className="inline-flex items-center space-x-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 pt-1"
                  >
                    <span>View Dossier</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>

              {/* Meta footer */}
              <div className="flex items-center justify-between text-[10px] text-slate-400 pt-2 border-t border-slate-100">
                <span>First recorded: {formattedDate(res.first_seen)}</span>
                {res.topic_name && <span>Topic: {res.topic_name}</span>}
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Blank state before searching */
        <div className="bg-white border border-slate-200 rounded-xl p-16 text-center space-y-3">
          <Search className="w-12 h-12 text-slate-300 mx-auto stroke-1" />
          <h3 className="text-base font-bold text-slate-700">Explore Indian Public Affairs</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Type keywords or semantic concepts above to retrieve verified events, government policies, and diplomatic summits.
          </p>
        </div>
      )}
    </div>
  );
}
