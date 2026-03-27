'use client';

import { useQuery } from '@tanstack/react-query';
import { getInspections, getDefectRates, getModelPerformance } from '@/lib/api';
import { LiveFeedPanel } from '@/components/live-feed/LiveFeedPanel';
import { DefectRateChart } from '@/components/analytics/DefectRateChart';

function StatCard({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string | number;
  sub?: string;
  accent?: string;
}) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <p className="text-xs font-medium uppercase tracking-wide text-gray-500">{label}</p>
      <p className={`mt-2 text-2xl font-bold ${accent ?? 'text-gray-800'}`}>{value}</p>
      {sub && <p className="mt-0.5 text-xs text-gray-400">{sub}</p>}
    </div>
  );
}

export default function DashboardPage() {
  const today = new Date().toDateString();

  const { data: inspectionsData } = useQuery({
    queryKey: ['inspections', 1, 100],
    queryFn: () => getInspections(1, 100),
    staleTime: 30_000,
  });

  const { data: defectRates } = useQuery({
    queryKey: ['defect-rates'],
    queryFn: getDefectRates,
    staleTime: 60_000,
  });

  const { data: modelPerf } = useQuery({
    queryKey: ['model-performance'],
    queryFn: getModelPerformance,
    staleTime: 60_000,
  });

  // Today's inspections
  const todayInspections =
    inspectionsData?.items.filter(
      (i) => new Date(i.timestamp).toDateString() === today
    ).length ?? 0;

  // Latest defect rate
  const latestRate = defectRates?.at(-1);
  const defectRateDisplay = latestRate
    ? `${(latestRate.defect_rate * 100).toFixed(1)}%`
    : '—';

  // Unique cameras
  const activeCameras = new Set(inspectionsData?.items.map((i) => i.camera_id) ?? []).size;

  // Avg latency across all models
  const avgLatency =
    modelPerf && modelPerf.length > 0
      ? (modelPerf.reduce((sum, m) => sum + m.avg_latency_ms, 0) / modelPerf.length).toFixed(0) +
        ' ms'
      : '—';

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          label="Inspections Today"
          value={todayInspections.toLocaleString()}
          sub="Total so far today"
        />
        <StatCard
          label="Defect Rate"
          value={defectRateDisplay}
          sub="Latest recorded"
          accent={
            latestRate && latestRate.defect_rate > 0.1 ? 'text-red-600' : 'text-green-600'
          }
        />
        <StatCard
          label="Active Cameras"
          value={activeCameras}
          sub="Cameras with recent activity"
        />
        <StatCard label="Avg Latency" value={avgLatency} sub="Across all models" />
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Chart spans 2 cols */}
        <div className="lg:col-span-2">
          <DefectRateChart />
        </div>

        {/* Live feed */}
        <div className="min-h-0 lg:h-[360px]">
          <LiveFeedPanel />
        </div>
      </div>
    </div>
  );
}
