'use client';

import { useState, useEffect } from 'react';
import EventCard from '@/components/EventCard';
import { fetchEvents, triggerIngestion } from '@/lib/api';
import { EventSummary, IngestionJobResponse } from '@/lib/types';
import { RefreshCw, Filter, Sparkles, AlertCircle } from 'lucide-react';

const CATEGORIES = [
  'All',
  'Current Affairs',
  'Parliament',
  'Economics',
  'Trade',
  'Defence',
  'Geopolitics',
];

export default function FeedPage() {
  const [events, setEvents] = useState<EventSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedCategory, setSelectedCategory] = useState('All');
  const [verificationFilter, setVerificationFilter] = useState('All');

  const [ingesting, setIngesting] = useState(false);
  const [ingestNotification, setIngestNotification] = useState<string | null>(
    null
  );

  const loadEvents = async () => {
    setLoading(true);
    setError(null);
    try {
      const vStatus =
        verificationFilter === 'All' ? undefined : verificationFilter;
      const data = await fetchEvents(vStatus);
      setEvents(data);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to event API baseline.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvents();
  }, [verificationFilter]);

  const handleIngest = async () => {
    setIngesting(true);
    setIngestNotification(null);
    try {
      const res: IngestionJobResponse = await triggerIngestion();
      setIngestNotification(res.message);
      // Reload events after triggering job
      setTimeout(loadEvents, 2000);
    } catch (err: any) {
      setIngestNotification(
        `Ingestion Trigger Failed: ${err.message || 'Network error'}`
      );
    } finally {
      setIngesting(false);
    }
  };

  const filteredEvents = events.filter((ev) => {
    if (selectedCategory === 'All') return true;
    return ev.category === selectedCategory;
  });

  return (
    <div className="space-y-8">
      {/* Header & Ingestion Action Bar */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Event Intelligence Feed
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Real-time Indian real-world occurrences supported by multi-source news evidence.
          </p>
        </div>

        <button
          onClick={handleIngest}
          disabled={ingesting}
          className="inline-flex items-center space-x-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-lg shadow-sm transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${ingesting ? 'animate-spin' : ''}`} />
          <span>{ingesting ? 'Triggering Ingestion...' : 'Trigger RSS Ingestion'}</span>
        </button>
      </div>

      {/* Ingestion Notification Banner */}
      {ingestNotification && (
        <div className="bg-indigo-50 border border-indigo-200 text-indigo-800 p-4 rounded-xl text-sm flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            <span>{ingestNotification}</span>
          </div>
          <button
            onClick={() => setIngestNotification(null)}
            className="text-xs font-semibold text-indigo-600 hover:underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Category Pills & Filters */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        {/* Domain Category Filter */}
        <div className="flex flex-wrap items-center gap-2">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors border ${
                selectedCategory === cat
                  ? 'bg-slate-900 text-white border-slate-900'
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Verification Status Filter */}
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={verificationFilter}
            onChange={(e) => setVerificationFilter(e.target.value)}
            aria-label="Filter events by verification status"
            className="bg-white border border-slate-200 rounded-lg text-xs font-medium px-3 py-1.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="All">All Verification Statuses</option>
            <option value="PENDING">PENDING (Single Source)</option>
            <option value="VERIFIED">VERIFIED (2+ Sources)</option>
            <option value="ARCHIVED">ARCHIVED</option>
          </select>
        </div>
      </div>

      {/* Event Grid & States */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div
              key={i}
              className="bg-white border border-slate-200 h-48 rounded-xl p-6"
            ></div>
          ))}
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 text-red-700 p-6 rounded-xl text-center space-y-2">
          <AlertCircle className="w-8 h-8 text-red-500 mx-auto" />
          <h3 className="font-semibold text-lg">Backend API Connection Error</h3>
          <p className="text-sm max-w-md mx-auto">{error}</p>
          <button
            onClick={loadEvents}
            className="mt-4 px-4 py-2 bg-red-600 text-white text-xs font-semibold rounded-lg hover:bg-red-700"
          >
            Retry Connection
          </button>
        </div>
      ) : filteredEvents.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-xl p-12 text-center space-y-3">
          <Sparkles className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="font-bold text-slate-800 text-lg">No Events Found</h3>
          <p className="text-sm text-slate-500 max-w-sm mx-auto">
            No events match the selected category or verification filter. Click "Trigger RSS Ingestion" above to fetch latest articles.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredEvents.map((event) => (
            <EventCard key={event.id} event={event} />
          ))}
        </div>
      )}
    </div>
  );
}
