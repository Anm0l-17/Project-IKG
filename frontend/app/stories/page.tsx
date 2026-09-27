'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { fetchStories } from '@/lib/api';
import { StorySummary } from '@/lib/types';
import {
  BookOpen,
  ShieldCheck,
  Clock,
  ChevronRight,
  RefreshCw,
  AlertCircle,
  Layers,
} from 'lucide-react';

const STATUS_FILTERS = ['All', 'VERIFIED', 'PENDING', 'ARCHIVED'];

const DOMAIN_COLORS: Record<string, string> = {
  Trade: 'bg-cyan-50 text-cyan-700 border-cyan-200',
  Parliament: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  Defence: 'bg-red-50 text-red-700 border-red-200',
  Economics: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  Geopolitics: 'bg-purple-50 text-purple-700 border-purple-200',
  'Current Affairs': 'bg-slate-50 text-slate-700 border-slate-200',
};

function StatusBadge({ status }: { status: string }) {
  if (status === 'VERIFIED') {
    return (
      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
        <ShieldCheck className="w-3 h-3" />
        <span>VERIFIED</span>
      </span>
    );
  }
  if (status === 'PENDING') {
    return (
      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
        <Clock className="w-3 h-3" />
        <span>DEVELOPING</span>
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-500 border border-slate-200">
      {status}
    </span>
  );
}

export default function StoriesPage() {
  const [stories, setStories] = useState<StorySummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState('All');

  const loadStories = async () => {
    try {
      setLoading(true);
      setError(null);
      const statusArg = statusFilter === 'All' ? undefined : statusFilter;
      const data = await fetchStories(undefined, undefined, statusArg);
      setStories(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load Stories.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStories();
  }, [statusFilter]);

  const formattedDate = (iso: string) =>
    new Date(iso).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-2">
        <div className="inline-flex items-center space-x-2 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-semibold border border-indigo-200">
          <BookOpen className="w-3.5 h-3.5" />
          <span>Long-Running Narratives</span>
        </div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Story Intelligence</h1>
        <p className="text-sm text-slate-500 max-w-2xl leading-relaxed">
          Stories group related verified Events into long-running narratives. A Story becomes{' '}
          <span className="text-emerald-600 font-semibold">VERIFIED</span> when at least 2 qualifying
          events are independently reported by different trusted publications.
        </p>
      </div>

      {/* Filters */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {STATUS_FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setStatusFilter(f)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                statusFilter === f
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
        <button
          onClick={loadStories}
          disabled={loading}
          className="inline-flex items-center space-x-1.5 text-xs text-slate-500 hover:text-slate-800 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-28 bg-white border border-slate-200 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-red-500 mx-auto" />
          <p className="text-sm font-medium text-red-800">{error}</p>
          <button
            onClick={loadStories}
            className="px-4 py-1.5 bg-red-600 text-white rounded-lg text-xs font-semibold hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      ) : stories.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-xl p-16 text-center space-y-3">
          <Layers className="w-10 h-10 text-slate-300 mx-auto stroke-1" />
          <p className="text-sm font-medium text-slate-500">No stories found.</p>
          <p className="text-xs text-slate-400">
            Stories are created automatically as Events are clustered into long-running narratives.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {stories.map((story) => {
            const domainColor =
              DOMAIN_COLORS[story.domain_name || ''] || 'bg-slate-50 text-slate-700 border-slate-200';

            return (
              <Link key={story.id} href={`/stories/${story.id}`}>
                <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md hover:border-slate-300 transition-all cursor-pointer group">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 space-y-2 min-w-0">
                      {/* Meta row */}
                      <div className="flex flex-wrap items-center gap-2">
                        {story.domain_name && (
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${domainColor}`}
                          >
                            {story.domain_name}
                          </span>
                        )}
                        {story.topic_name && (
                          <span className="text-xs text-slate-500 font-medium truncate max-w-[200px]">
                            {story.topic_name}
                          </span>
                        )}
                        <StatusBadge status={story.status} />
                      </div>

                      {/* Title */}
                      <h3 className="text-base font-bold text-slate-900 leading-snug group-hover:text-blue-700 transition-colors">
                        {story.title}
                      </h3>

                      {story.description && (
                        <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
                          {story.description}
                        </p>
                      )}
                    </div>

                    {/* Stats */}
                    <div className="flex-shrink-0 text-right space-y-2">
                      <div className="text-xs font-semibold text-slate-900">
                        {story.event_count}{' '}
                        <span className="font-normal text-slate-500">
                          event{story.event_count !== 1 ? 's' : ''}
                        </span>
                      </div>
                      <div className="text-[10px] text-slate-400">
                        Updated {formattedDate(story.updated_at)}
                      </div>
                      <ChevronRight className="w-4 h-4 text-slate-400 ml-auto group-hover:text-blue-600 transition-colors" />
                    </div>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
