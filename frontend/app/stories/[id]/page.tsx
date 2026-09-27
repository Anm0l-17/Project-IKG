'use client';

import React, { useState, useEffect, use } from 'react';
import Link from 'next/link';
import { fetchStoryById } from '@/lib/api';
import { StoryDetail, StoryTimelineItem } from '@/lib/types';
import {
  ArrowLeft,
  ShieldCheck,
  Clock,
  AlertCircle,
  BookOpen,
  Newspaper,
  CheckCircle2,
  Network,
  Calendar,
  BarChart3,
} from 'lucide-react';

interface StoryDetailPageProps {
  params: Promise<{ id: string }>;
}

function VerificationBadge({ status }: { status: string }) {
  if (status === 'VERIFIED') {
    return (
      <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
        <ShieldCheck className="w-3.5 h-3.5" />
        <span>VERIFIED — Multi-Source Consensus</span>
      </span>
    );
  }
  if (status === 'PENDING') {
    return (
      <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">
        <Clock className="w-3.5 h-3.5" />
        <span>DEVELOPING — Awaiting Corroboration</span>
      </span>
    );
  }
  return (
    <span className="inline-flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-600 border border-slate-200">
      {status}
    </span>
  );
}

function EventVerificationIcon({ status }: { status: string }) {
  if (status === 'VERIFIED') return <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0" />;
  if (status === 'DEVELOPING' || status === 'PENDING') return <Clock className="w-4 h-4 text-amber-500 flex-shrink-0" />;
  return <AlertCircle className="w-4 h-4 text-slate-400 flex-shrink-0" />;
}

export default function StoryDetailPage({ params }: StoryDetailPageProps) {
  const resolvedParams = use(params);
  const storyId = resolvedParams.id;

  const [story, setStory] = useState<StoryDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadStory() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchStoryById(storyId);
        setStory(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load Story.');
      } finally {
        setLoading(false);
      }
    }
    loadStory();
  }, [storyId]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6 animate-pulse">
        <div className="h-5 w-32 bg-slate-200 rounded" />
        <div className="h-48 bg-white border border-slate-200 rounded-xl" />
        <div className="h-80 bg-white border border-slate-200 rounded-xl" />
      </div>
    );
  }

  if (error || !story) {
    return (
      <div className="max-w-xl mx-auto bg-red-50 border border-red-200 text-red-700 p-8 rounded-xl text-center space-y-4">
        <AlertCircle className="w-10 h-10 text-red-500 mx-auto" />
        <h2 className="text-xl font-bold">Story Not Found</h2>
        <p className="text-sm">{error || 'The requested story does not exist.'}</p>
        <Link href="/stories" className="inline-block px-4 py-2 bg-slate-900 text-white text-xs font-semibold rounded-lg">
          &larr; Back to Stories
        </Link>
      </div>
    );
  }

  const formattedDate = (iso: string) =>
    new Date(iso).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Breadcrumb */}
      <Link
        href="/stories"
        className="inline-flex items-center space-x-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Story Intelligence</span>
      </Link>

      {/* Story Header */}
      <div className="bg-white border border-slate-200 rounded-xl p-8 shadow-sm space-y-5">
        {/* Meta badges */}
        <div className="flex flex-wrap items-center gap-2.5">
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
            <BookOpen className="w-3 h-3" />
            <span>Narrative Story</span>
          </span>
          {story.domain_name && (
            <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-slate-900 text-white">
              {story.domain_name}
            </span>
          )}
          {story.topic_name && (
            <span className="text-xs text-slate-500 font-medium">{story.topic_name}</span>
          )}
          <VerificationBadge status={story.status} />
        </div>

        {/* Title */}
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight leading-tight">
          {story.title}
        </h1>

        {/* Description */}
        {story.description && (
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-5">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
              Narrative Overview
            </h3>
            <p className="text-slate-700 text-sm leading-relaxed">{story.description}</p>
          </div>
        )}

        {/* Stats row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-slate-100">
          <div className="space-y-0.5">
            <div className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Events</div>
            <div className="text-xl font-bold text-slate-900">{story.event_count}</div>
          </div>
          <div className="space-y-0.5">
            <div className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Sources</div>
            <div className="text-xl font-bold text-slate-900">{story.source_count}</div>
          </div>
          <div className="space-y-0.5">
            <div className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Started</div>
            <div className="text-sm font-semibold text-slate-700">{formattedDate(story.created_at)}</div>
          </div>
          <div className="space-y-0.5">
            <div className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Updated</div>
            <div className="text-sm font-semibold text-slate-700">{formattedDate(story.updated_at)}</div>
          </div>
        </div>

        {/* Source diversity */}
        {story.sources.length > 0 && (
          <div className="pt-2">
            <div className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider mb-2">
              Contributing Publications
            </div>
            <div className="flex flex-wrap gap-2">
              {story.sources.map((src) => (
                <span
                  key={src}
                  className="inline-flex items-center space-x-1 px-2.5 py-1 bg-slate-100 text-slate-700 rounded-full text-xs font-medium border border-slate-200"
                >
                  <Newspaper className="w-3 h-3 text-slate-400" />
                  <span>{src}</span>
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Narrative Timeline */}
      <div className="bg-white border border-slate-200 rounded-xl p-8 shadow-sm space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center space-x-2">
            <Calendar className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900">Narrative Progression</h2>
          </div>
          <span className="text-xs font-semibold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full">
            {story.timeline.length} events in sequence
          </span>
        </div>

        {story.timeline.length === 0 ? (
          <div className="text-center py-8 space-y-2 text-slate-400">
            <BarChart3 className="w-8 h-8 mx-auto stroke-1" />
            <p className="text-sm">No events recorded in this story timeline yet.</p>
          </div>
        ) : (
          <div className="relative border-l-2 border-indigo-200 ml-4 space-y-8 pl-8">
            {story.timeline.map((item: StoryTimelineItem) => (
              <div key={item.event_id} className="relative group">
                {/* Timeline dot */}
                <div className="absolute -left-[37px] top-1 flex items-center justify-center w-6 h-6 rounded-full bg-white border-2 border-indigo-400 shadow-sm">
                  <span className="text-[9px] font-bold text-indigo-600">{item.sequence}</span>
                </div>

                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3 group-hover:border-slate-300 transition-colors">
                  {/* Header */}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start space-x-2 flex-1 min-w-0">
                      <EventVerificationIcon status={item.verification_status} />
                      <div className="min-w-0">
                        <Link
                          href={`/events/${item.event_id}`}
                          className="text-sm font-bold text-slate-900 hover:text-blue-700 transition-colors leading-snug line-clamp-2"
                        >
                          {item.title}
                        </Link>
                      </div>
                    </div>
                    <div className="flex-shrink-0 text-right space-y-1">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-white border border-slate-200 text-slate-600">
                        {item.category}
                      </span>
                    </div>
                  </div>

                  {/* Summary */}
                  {item.summary && (
                    <p className="text-xs text-slate-600 leading-relaxed line-clamp-3">{item.summary}</p>
                  )}

                  {/* Footer */}
                  <div className="flex items-center justify-between text-[10px] text-slate-400">
                    <span>
                      {new Date(item.first_seen).toLocaleDateString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric',
                      })}
                    </span>
                    {item.sources.length > 0 && (
                      <div className="flex items-center space-x-1">
                        <Newspaper className="w-3 h-3" />
                        <span>{item.sources.slice(0, 2).join(', ')}</span>
                        {item.sources.length > 2 && <span>+{item.sources.length - 2}</span>}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Knowledge Graph CTA */}
      <div className="bg-gradient-to-r from-slate-50 to-indigo-50 border border-indigo-100 rounded-xl p-5 flex items-center justify-between">
        <div className="space-y-0.5">
          <p className="text-sm font-semibold text-slate-800">
            Explore this story in the Knowledge Graph
          </p>
          <p className="text-xs text-slate-500">
            See how these events are interconnected with other Indian public affairs.
          </p>
        </div>
        <Link
          href="/graph"
          className="inline-flex items-center space-x-1.5 px-4 py-2 bg-slate-900 text-white text-xs font-semibold rounded-lg hover:bg-slate-800 transition-colors shadow-sm flex-shrink-0"
        >
          <Network className="w-3.5 h-3.5" />
          <span>Open Graph</span>
        </Link>
      </div>
    </div>
  );
}
