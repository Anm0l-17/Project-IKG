'use client';

import { useState, useEffect, use } from 'react';
import Link from 'next/link';
import { fetchEventById } from '@/lib/api';
import { EventDetail } from '@/lib/types';
import {
  ArrowLeft,
  Clock,
  CheckCircle2,
  AlertCircle,
  Layers,
  FileText,
  Calendar,
  Sparkles,
} from 'lucide-react';

interface EventDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function EventDetailPage({ params }: EventDetailPageProps) {
  const resolvedParams = use(params);
  const eventId = resolvedParams.id;

  const [event, setEvent] = useState<EventDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadEventDetail() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchEventById(eventId);
        setEvent(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load event details.');
      } finally {
        setLoading(false);
      }
    }
    loadEventDetail();
  }, [eventId]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6 animate-pulse">
        <div className="h-6 w-32 bg-slate-200 rounded"></div>
        <div className="h-40 bg-white border border-slate-200 rounded-xl"></div>
        <div className="h-64 bg-white border border-slate-200 rounded-xl"></div>
      </div>
    );
  }

  if (error || !event) {
    return (
      <div className="max-w-xl mx-auto bg-red-50 border border-red-200 text-red-700 p-8 rounded-xl text-center space-y-4">
        <AlertCircle className="w-10 h-10 text-red-500 mx-auto" />
        <h2 className="text-xl font-bold">Event Not Found</h2>
        <p className="text-sm">{error || 'The requested event does not exist.'}</p>
        <Link
          href="/feed"
          className="inline-block px-4 py-2 bg-slate-900 text-white text-xs font-semibold rounded-lg"
        >
          &larr; Back to Event Feed
        </Link>
      </div>
    );
  }

  const formattedFirstSeen = new Date(event.first_seen).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Navigation Breadcrumb */}
      <div>
        <Link
          href="/feed"
          className="inline-flex items-center space-x-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Event Intelligence Feed</span>
        </Link>
      </div>

      {/* Main Event Header Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-8 shadow-sm space-y-6">
        {/* Badges Bar */}
        <div className="flex flex-wrap items-center gap-3">
          <span className="px-3 py-1 bg-slate-900 text-white rounded-full text-xs font-semibold">
            {event.category}
          </span>

          {event.is_developing ? (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-sky-50 text-sky-700 border border-sky-200">
              <span className="w-2 h-2 rounded-full bg-sky-500 animate-pulse"></span>
              <span>DEVELOPING (Single Source Report)</span>
            </span>
          ) : event.verification_status === 'VERIFIED' ? (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>VERIFIED (Multi-Source Consensus)</span>
            </span>
          ) : (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
              <AlertCircle className="w-4 h-4 text-amber-600" />
              <span>{event.verification_status}</span>
            </span>
          )}

          <span className="inline-flex items-center space-x-1 text-xs text-slate-500 font-medium">
            <Layers className="w-4 h-4 text-slate-400" />
            <span>Grouping: {event.grouping_status}</span>
          </span>
        </div>

        {/* Title & Summary */}
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight leading-tight">
          {event.canonical_title}
        </h1>

        {event.summary && (
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-5">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
              Event Intelligence Context
            </h3>
            <p className="text-slate-700 text-sm leading-relaxed">{event.summary}</p>
          </div>
        )}

        {/* Event Provenance & Metadata */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-slate-100 text-xs text-slate-500">
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-slate-400" />
            <span>First Discovered: {formattedFirstSeen}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-slate-400" />
            <span>Knowledge Confidence Score: {event.knowledge_score}</span>
          </div>
        </div>
      </div>

      {/* Chronological Timeline Section */}
      <div className="bg-white border border-slate-200 rounded-xl p-8 shadow-sm space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center space-x-2">
            <Calendar className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900">Event Chronological Timeline</h2>
          </div>
          <span className="text-xs font-semibold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full">
            {event.timeline_entries.length} Timeline Entries
          </span>
        </div>

        {event.timeline_entries.length === 0 ? (
          <div className="text-center py-8 space-y-2 text-slate-400">
            <FileText className="w-8 h-8 mx-auto" />
            <p className="text-sm">No secondary timeline entries attached yet.</p>
          </div>
        ) : (
          <div className="relative border-l-2 border-slate-200 ml-4 space-y-8 pl-6">
            {event.timeline_entries.map((entry) => (
              <div key={entry.id} className="relative group">
                {/* Timeline Dot */}
                <div className="absolute -left-[31px] top-1.5 w-3.5 h-3.5 rounded-full bg-white border-2 border-indigo-600 group-hover:bg-indigo-600 transition-colors"></div>

                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
                    <span>Sequence #{entry.sequence}</span>
                    <span>
                      {new Date(entry.published_at).toLocaleDateString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric',
                      })}
                    </span>
                  </div>

                  <h4 className="text-base font-bold text-slate-900">
                    {entry.title}
                  </h4>

                  {entry.summary && (
                    <p className="text-xs text-slate-600 leading-relaxed">
                      {entry.summary}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
