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
  primary_story_id?: string;
}

export interface EventDetail extends EventSummary {
  timeline_entries: TimelineEntry[];
}

export interface IngestionJobResponse {
  message: string;
  status: string;
}

export interface GraphNode {
  id: string;
  label: string;
  type: "EVENT" | "ENTITY";
  category?: string;
  status?: string;
  importance?: number;
  is_central?: boolean;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  confidence: number;
  reasoning?: string;
}

export interface GraphResponse {
  central_event_id?: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  node_count: number;
  edge_count: number;
}

export interface StorySummary {
  id: string;
  title: string;
  slug: string;
  description?: string;
  status: string;
  topic_id: string;
  topic_name?: string;
  domain_name?: string;
  event_count: number;
  created_at: string;
  updated_at: string;
}

export interface StoryTimelineItem {
  sequence: number;
  event_id: string;
  title: string;
  category: string;
  first_seen: string;
  verification_status: string;
  summary?: string;
  sources: string[];
  source_count: number;
}

export interface StoryDetail extends StorySummary {
  sources: string[];
  source_count: number;
  timeline: StoryTimelineItem[];
}

export interface SearchResultItem {
  id: string;
  title: string;
  slug: string;
  category: string;
  subcategory?: string;
  summary?: string;
  highlight_snippet?: string;
  knowledge_score: number;
  verification_status: string;
  grouping_status: string;
  primary_story_id?: string;
  topic_name?: string;
  domain_name?: string;
  first_seen: string;
  last_updated: string;
  relevance_score: number;
  lexical_score: number;
  semantic_score: number;
  match_type: 'HYBRID' | 'SEMANTIC' | 'LEXICAL' | 'RELEVANCE';
}

export interface SearchResponse {
  query: string;
  mode: string;
  total_results: number;
  results: SearchResultItem[];
}



