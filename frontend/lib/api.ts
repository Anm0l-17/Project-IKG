import { EventSummary, EventDetail, IngestionJobResponse } from './types';

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
