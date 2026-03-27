'use client';

import { useQuery } from '@tanstack/react-query';
import { getModelPerformance } from '@/lib/api';

function MetricCell({ value, isLatency = false }: { value: number; isLatency?: boolean }) {
  const display = isLatency ? `${value.toFixed(1)} ms` : `${(value * 100).toFixed(1)}%`;
  return <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-700">{display}</td>;
}

export function ModelPerformanceTable() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['model-performance'],
    queryFn: getModelPerformance,
    staleTime: 60_000,
  });

  if (isLoading) {
    return (
      <div className="flex h-32 items-center justify-center rounded-xl border border-gray-200 bg-white text-sm text-gray-400">
        Loading performance data…
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex h-32 items-center justify-center rounded-xl border border-red-200 bg-red-50 text-sm text-red-600">
        Failed to load model performance.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
      <div className="border-b border-gray-100 px-5 py-4">
        <h2 className="text-sm font-semibold text-gray-800">Model Performance</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 text-left">
              {['Model', 'Accuracy', 'Precision', 'Recall', 'F1 Score', 'Avg Latency', 'Inferences'].map(
                (col) => (
                  <th
                    key={col}
                    className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-gray-500"
                  >
                    {col}
                  </th>
                )
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {data.map((model) => (
              <tr key={model.model_name} className="hover:bg-gray-50">
                <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-gray-800">
                  {model.model_name}
                </td>
                <MetricCell value={model.accuracy} />
                <MetricCell value={model.precision} />
                <MetricCell value={model.recall} />
                <MetricCell value={model.f1_score} />
                <MetricCell value={model.avg_latency_ms} isLatency />
                <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-700">
                  {model.total_inferences.toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
