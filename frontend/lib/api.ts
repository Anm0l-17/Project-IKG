import {
  EventSummary,
  EventDetail,
  IngestionJobResponse,
  GraphResponse,
  StorySummary,
  StoryDetail,
  SearchResponse,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function fetchEvents(
  verificationStatus?: string,
  groupingStatus?: string
): Promise<EventSummary[]> {
  const params = new URLSearchParams();
  if (verificationStatus) params.append('verification_status', verificationStatus);
  if (groupingStatus) params.append('grouping_status', groupingStatus);
  params.append('limit', '50');

  const url = `${API_BASE_URL}/events?${params.toString()}`;
  const response = await fetch(url, { cache: 'no-store' });

  if (!response.ok) {
    throw new Error(`Failed to fetch events: ${response.statusText}`);
  }

  return response.json();
}

export async function fetchEventById(id: string): Promise<EventDetail> {
  const url = `${API_BASE_URL}/events/${id}`;
  const response = await fetch(url, { cache: 'no-store' });

  if (!response.ok) {
    throw new Error(`Failed to fetch event detail: ${response.statusText}`);
  }

  return response.json();
}

export async function fetchGlobalGraph(category?: string, limit: number = 40): Promise<GraphResponse> {
  const params = new URLSearchParams();
  if (category) params.append('category', category);
  params.append('limit', limit.toString());

  const url = `${API_BASE_URL}/graph?${params.toString()}`;
  const response = await fetch(url, { cache: 'no-store' });

  if (!response.ok) {
    throw new Error(`Failed to fetch global graph: ${response.statusText}`);
  }

  return response.json();
}

export async function fetchEventGraph(eventId: string): Promise<GraphResponse> {
  const url = `${API_BASE_URL}/graph/event/${eventId}`;
  const response = await fetch(url, { cache: 'no-store' });

  if (!response.ok) {
    throw new Error(`Failed to fetch event graph: ${response.statusText}`);
  }

  return response.json();
}

export async function triggerIngestion(): Promise<IngestionJobResponse> {
  const url = `${API_BASE_URL}/events/ingest`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to trigger ingestion: ${response.statusText}`);
  }

  return response.json();
}

export async function fetchStories(
  topicId?: string,
  domainId?: string,
  status?: string
): Promise<StorySummary[]> {
  const params = new URLSearchParams();
  if (topicId) params.append('topic_id', topicId);
  if (domainId) params.append('domain_id', domainId);
  if (status) params.append('status_filter', status);
  params.append('limit', '50');

  const url = `${API_BASE_URL}/stories?${params.toString()}`;
  const response = await fetch(url, { cache: 'no-store' });

  if (!response.ok) {
    throw new Error(`Failed to fetch stories: ${response.statusText}`);
  }

  return response.json();
}

export async function fetchStoryById(id: string): Promise<StoryDetail> {
  const url = `${API_BASE_URL}/stories/${id}`;
  const response = await fetch(url, { cache: 'no-store' });

  if (!response.ok) {
    throw new Error(`Failed to fetch story detail: ${response.statusText}`);
  }

  return response.json();
}

export async function searchEvents(
  query: string,
  options?: {
    mode?: 'hybrid' | 'semantic' | 'lexical';
    category?: string;
    verificationStatus?: string;
    topicId?: string;
    limit?: number;
    offset?: number;
  }
): Promise<SearchResponse> {
  const params = new URLSearchParams();
  params.append('q', query);
  if (options?.mode) params.append('mode', options.mode);
  if (options?.category) params.append('category', options.category);
  if (options?.verificationStatus) params.append('verification_status', options.verificationStatus);
  if (options?.topicId) params.append('topic_id', options.topicId);
  if (options?.limit) params.append('limit', options.limit.toString());
  if (options?.offset) params.append('offset', options.offset.toString());

  const url = `${API_BASE_URL}/search?${params.toString()}`;
  const response = await fetch(url, { cache: 'no-store' });

  if (!response.ok) {
    throw new Error(`Failed to execute search: ${response.statusText}`);
  }

  return response.json();
}


