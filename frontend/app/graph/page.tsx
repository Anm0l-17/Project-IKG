'use client';

import React, { useState, useEffect } from 'react';
import { fetchGlobalGraph } from '@/lib/api';
import { GraphResponse } from '@/lib/types';
import KnowledgeGraphViewer from '@/components/KnowledgeGraphViewer';
import { Network, RefreshCw, Layers, ShieldCheck, Sparkles, AlertCircle } from 'lucide-react';

const CATEGORIES = [
  'All',
  'Current Affairs',
  'Parliament',
  'Economics',
  'Trade',
  'Defence',
  'Geopolitics',
];

export default function GraphPage() {
  const [graphData, setGraphData] = useState<GraphResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');

  useEffect(() => {
    async function loadGraph() {
      try {
        setLoading(true);
        setError(null);
        const cat = selectedCategory === 'All' ? undefined : selectedCategory;
        const data = await fetchGlobalGraph(cat, 50);
        setGraphData(data);
      } catch (err: unknown) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('Failed to load Knowledge Graph data.');
        }
      } finally {
        setLoading(false);
      }
    }
    loadGraph();
  }, [selectedCategory]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-semibold border border-blue-200 mb-2">
            <Network className="w-3.5 h-3.5" />
            <span>Deterministic Knowledge Network</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            India Knowledge Graph Explorer
          </h1>
          <p className="text-sm text-slate-600 max-w-2xl mt-1 leading-relaxed">
            Traverse interconnected Indian public affairs. Events are linked via validated temporal sequence (<span className="text-blue-600 font-semibold">PRECEDES</span>), causal dependencies (<span className="text-red-600 font-semibold">CAUSES</span>), and topical affinity (<span className="text-emerald-600 font-semibold">RELATED_TO</span>).
          </p>
        </div>

        <button
          onClick={async () => {
            try {
              setLoading(true);
              setError(null);
              const cat = selectedCategory === 'All' ? undefined : selectedCategory;
              const data = await fetchGlobalGraph(cat, 50);
              setGraphData(data);
            } catch (err: unknown) {
              if (err instanceof Error) {
                setError(err.message);
              } else {
                setError('Failed to load Knowledge Graph data.');
              }
            } finally {
              setLoading(false);
            }
          }}
          disabled={loading}
          className="inline-flex items-center space-x-2 px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-medium hover:bg-slate-800 disabled:opacity-50 transition-colors shadow-sm self-start md:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Graph</span>
        </button>
      </div>

      {/* Category Pills */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1">
        {CATEGORIES.map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
              selectedCategory === cat
                ? 'bg-slate-900 text-white shadow-sm'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Main Graph Viewer or States */}
      {loading ? (
        <div className="bg-white border border-slate-200 rounded-xl p-16 flex flex-col items-center justify-center space-y-3 shadow-sm min-h-[500px]">
          <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
          <p className="text-sm font-medium text-slate-600">Synthesizing knowledge graph projection...</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-red-500 mx-auto" />
          <p className="text-sm font-medium text-red-800">{error}</p>
          <button
            onClick={async () => {
              try {
                setLoading(true);
                setError(null);
                const cat = selectedCategory === 'All' ? undefined : selectedCategory;
                const data = await fetchGlobalGraph(cat, 50);
                setGraphData(data);
              } catch (err: unknown) {
                if (err instanceof Error) {
                  setError(err.message);
                } else {
                  setError('Failed to load Knowledge Graph data.');
                }
              } finally {
                setLoading(false);
              }
            }}
            className="px-4 py-1.5 bg-red-600 text-white rounded-lg text-xs font-semibold hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      ) : graphData ? (
        <KnowledgeGraphViewer graph={graphData} height="620px" />
      ) : null}

      {/* Architectural Guarantee Notes */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border border-slate-200 p-4 rounded-xl shadow-sm space-y-1.5">
          <div className="flex items-center space-x-2 text-slate-900 font-semibold text-xs">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>AI Proposes, Rules Validate</span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            No AI model can arbitrarily fabricate edges. All graph links require deterministic verification, entity overlap, and multi-source corroboration.
          </p>
        </div>

        <div className="bg-white border border-slate-200 p-4 rounded-xl shadow-sm space-y-1.5">
          <div className="flex items-center space-x-2 text-slate-900 font-semibold text-xs">
            <Sparkles className="w-4 h-4 text-indigo-600" />
            <span>Bounded Explanations</span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Every edge records confidence score, evidence count, and explicit reasoning so users know precisely why two events are connected.
          </p>
        </div>

        <div className="bg-white border border-slate-200 p-4 rounded-xl shadow-sm space-y-1.5">
          <div className="flex items-center space-x-2 text-slate-900 font-semibold text-xs">
            <Layers className="w-4 h-4 text-blue-600" />
            <span>Events First, Articles Evidence</span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Graph nodes represent real-world occurrences and official entities. News articles remain immutable evidence behind the nodes.
          </p>
        </div>
      </div>
    </div>
  );
}
