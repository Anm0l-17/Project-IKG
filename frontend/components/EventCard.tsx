import Link from 'next/link';
import { EventSummary } from '@/lib/types';
import { Clock, CheckCircle2, AlertCircle, Layers, BookOpen } from 'lucide-react';

interface EventCardProps {
  event: EventSummary;
}

const CATEGORY_STYLES: Record<string, string> = {
  Parliament: 'bg-purple-50 text-purple-700 border-purple-200',
  Economics: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  Trade: 'bg-blue-50 text-blue-700 border-blue-200',
  Defence: 'bg-amber-50 text-amber-700 border-amber-200',
  Geopolitics: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  'Current Affairs': 'bg-slate-100 text-slate-700 border-slate-200',
};

export default function EventCard({ event }: EventCardProps) {
  const categoryStyle =
    CATEGORY_STYLES[event.category] || CATEGORY_STYLES['Current Affairs'];

  const formattedDate = new Date(event.first_seen).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between space-y-4">
      <div className="space-y-3">
        {/* Badges Row */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Domain Category Badge */}
          <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${categoryStyle}`}
          >
            {event.category}
          </span>

          {/* Verification Status Badge */}
          {event.is_developing ? (
            <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-sky-50 text-sky-700 border border-sky-200">
              <span className="w-1.5 h-1.5 rounded-full bg-sky-500 animate-pulse"></span>
              <span>DEVELOPING (Single Source)</span>
            </span>
          ) : event.verification_status === 'VERIFIED' ? (
            <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>VERIFIED</span>
            </span>
          ) : (
            <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
              <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
              <span>{event.verification_status}</span>
            </span>
          )}

          {/* Grouping Status */}
          <span className="inline-flex items-center space-x-1 text-xs text-slate-500 font-medium">
            <Layers className="w-3.5 h-3.5 text-slate-400" />
            <span>{event.grouping_status}</span>
          </span>

          {/* Story Badge — shown when event is part of a narrative */}
          {event.grouping_status === 'GROUPED' && event.primary_story_id && (
            <Link
              href={`/stories/${event.primary_story_id}`}
              className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 hover:bg-indigo-100 transition-colors"
              onClick={(e) => e.stopPropagation()}
            >
              <BookOpen className="w-3 h-3" />
              <span>Part of a Story</span>
            </Link>
          )}
        </div>

        {/* Title */}
        <h3 className="text-lg font-bold text-slate-900 leading-snug hover:text-indigo-600 transition-colors">
          <Link href={`/events/${event.id}`}>{event.canonical_title}</Link>
        </h3>

        {/* Summary Snippet */}
        {event.summary && (
          <p className="text-sm text-slate-600 line-clamp-3 leading-relaxed">
            {event.summary}
          </p>
        )}
      </div>

      {/* Footer Meta */}
      <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <div className="flex items-center space-x-1.5">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>{formattedDate}</span>
        </div>
        <Link
          href={`/events/${event.id}`}
          className="font-semibold text-indigo-600 hover:text-indigo-800 transition-colors"
        >
          View Event Details &rarr;
        </Link>
      </div>
    </div>
  );
}
