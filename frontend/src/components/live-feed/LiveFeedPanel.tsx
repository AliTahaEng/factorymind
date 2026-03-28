'use client';

import { useLiveFeed } from '@/hooks/useLiveFeed';

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const barColor = value > 0.5 ? 'bg-red-500' : 'bg-green-500';
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-full rounded-full bg-gray-200">
        <div
          className={`h-2 rounded-full transition-all ${barColor}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-10 text-right text-xs font-medium text-gray-700">{pct}%</span>
    </div>
  );
}

export function LiveFeedPanel() {
  const { events, isConnected } = useLiveFeed();

  return (
    <div className="flex h-full flex-col rounded-xl border border-gray-200 bg-white shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3">
        <h2 className="text-sm font-semibold text-gray-800">Live Feed</h2>
        <span
          className={`flex items-center gap-1.5 text-xs font-medium ${
            isConnected ? 'text-green-600' : 'text-gray-400'
          }`}
        >
          <span
            className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-300'}`}
          />
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>

      {/* Event list */}
      <div className="flex-1 overflow-y-auto">
        {events.length === 0 ? (
          <div className="flex h-full items-center justify-center text-sm text-gray-400">
            Waiting for events…
          </div>
        ) : (
          <ul className="divide-y divide-gray-50">
            {events.map((event) => (
              <li key={event.inspection_id} className="px-4 py-3 hover:bg-gray-50">
                <div className="mb-1 flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-700">
                    {event.inspection_id.slice(0, 8)}…
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <ConfidenceBar value={event.confidence} />
                {event.defect_detected && event.defect_type && (
                  <div className="mt-1.5 flex flex-wrap gap-1">
                    <span className="inline-flex items-center gap-1 rounded-full border border-red-300 bg-red-100 px-2.5 py-0.5 text-xs font-semibold text-red-800">
                      {event.defect_type}
                      <span className="opacity-75">({(event.confidence * 100).toFixed(0)}%)</span>
                    </span>
                  </div>
                )}
                {!event.defect_detected && (
                  <span className="mt-1 inline-block text-xs text-green-600 font-medium">✓ OK</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
