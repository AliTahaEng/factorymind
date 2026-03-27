'use client';

import { useEffect, useState, useRef } from 'react';
import { wsManager } from '@/lib/websocket';
import { useAuthStore } from '@/store/auth';
import type { LiveFeedEvent } from '@/types/api';

const MAX_EVENTS = 50;

export function useLiveFeed() {
  const token = useAuthStore((s) => s.token);
  const [events, setEvents] = useState<LiveFeedEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<LiveFeedEvent | null>(null);
  const wsRef = useRef(wsManager);

  useEffect(() => {
    if (!token) return;

    const manager = wsRef.current;

    // We approximate connection status via presence of messages
    const removeMessage = manager.onMessage((data) => {
      const event = data as LiveFeedEvent;
      setIsConnected(true);
      setLastEvent(event);
      setEvents((prev) => [event, ...prev].slice(0, MAX_EVENTS));
    });

    const removeError = manager.onError(() => {
      setIsConnected(false);
    });

    manager.connect(token);

    return () => {
      removeMessage();
      removeError();
      manager.disconnect();
      setIsConnected(false);
    };
  }, [token]);

  return { events, isConnected, lastEvent };
}
