'use client';

import { useEffect, useState } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface EventSummary {
  id: string;
  title: string;
  summary?: string;
}

interface TimelineEntry {
  timestamp: string; // ISO datetime
  title: string;
  status: string;
  source?: string;
  evidence?: string;
}

interface ApiEvent {
  id: string;
  canonical_title: string;
  summary?: string;
}

interface ApiTimelineEntry {
  published_at: string;
  title: string;
  summary: string;
}

export default function TimelinePage() {
  const [events, setEvents] = useState<EventSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string>('');
  const [timeline, setTimeline] = useState<TimelineEntry[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  // Load list of events on mount
  useEffect(() => {
    fetch(`${API_BASE_URL}/events?limit=100`)
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to fetch events: ${res.status}`);
        return res.json() as Promise<ApiEvent[]>;
      })
      .then((data) => {
        const list = data.map((e) => ({
          id: e.id,
          title: e.canonical_title,
          summary: e.summary,
        }));
        setEvents(list);
      })
      .catch((err) => console.error('Failed to fetch events', err));
  }, []);

  // Load timeline whenever a new event is selected
  useEffect(() => {
    if (!selectedId) return;
    setLoading(true);
    fetch(`${API_BASE_URL}/events/${selectedId}/timeline`)
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to fetch timeline: ${res.status}`);
        return res.json() as Promise<ApiTimelineEntry[]>;
      })
      .then((data) => {
        const entries: TimelineEntry[] = data.map((e) => ({
          timestamp: e.published_at,
          title: e.title,
          status: 'Published',
          evidence: e.summary,
        }));
        entries.sort(
          (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
        );
        setTimeline(entries);
      })
      .catch((err) => console.error('Failed to fetch timeline', err))
      .finally(() => setLoading(false));
  }, [selectedId]);

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">Timelines</h1>
      <div className="flex gap-4">
        {/* Event selector */}
        <select
          className="border border-slate-300 rounded p-2"
          value={selectedId}
          onChange={(e) => setSelectedId(e.target.value)}
        >
          <option value="">Select an event…</option>
          {events.map((ev) => (
            <option key={ev.id} value={ev.id}>
              {ev.title}{ev.summary ? ` — ${ev.summary}` : ''}
            </option>
          ))}
        </select>
      </div>

      {loading && <p>Loading timeline…</p>}

      {timeline.length > 0 && (
        <ul className="border-l border-slate-300 ml-4 space-y-4">
          {timeline.map((entry, idx) => (
            <li key={idx} className="relative pl-4">
              <div className="absolute left-0 top-0 w-3 h-3 bg-slate-500 rounded-full" />
              <time className="text-xs text-slate-500">
                {new Date(entry.timestamp).toLocaleString()}
              </time>
              <div className="font-medium">{entry.title}</div>
              <div className="text-sm text-slate-600">Status: {entry.status}</div>
              {entry.source && <div className="text-sm text-slate-600">Source: {entry.source}</div>}
              {entry.evidence && <div className="text-sm text-slate-600">Evidence: {entry.evidence}</div>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
