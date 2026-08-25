export interface TimelineEntry {
  id: string;
  sequence: number;
  title: string;
  summary?: string;
  published_at: string;
  importance: number;
  source_count: number;
}

export interface EventSummary {
  id: string;
  canonical_title: string;
  slug: string;
  category: string;
  subcategory?: string;
  summary?: string;
  knowledge_score: number;
  grouping_status: string;
  verification_status: string;
  status: string;
  is_developing: boolean;
  first_seen: string;
  last_updated: string;
}

export interface EventDetail extends EventSummary {
  timeline_entries: TimelineEntry[];
}

export interface IngestionJobResponse {
  message: string;
  status: string;
}
