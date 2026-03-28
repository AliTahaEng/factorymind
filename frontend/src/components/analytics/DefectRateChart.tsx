'use client';

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { useQuery } from '@tanstack/react-query';
import { getDefectRates } from '@/lib/api';

export function DefectRateChart() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['defect-rates'],
    queryFn: getDefectRates,
    staleTime: 60_000,
  });

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-gray-200 bg-white text-sm text-gray-400">
        Loading chart…
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-red-200 bg-red-50 text-sm text-red-600">
        Failed to load defect rate data.
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-gray-200 bg-white text-sm text-gray-400">
        No defect data yet. Start the camera simulator to generate data.
      </div>
    );
  }

  const chartData = data.map((d) => ({
    date: typeof d.period === 'string' ? d.period.slice(0, 10) : String(d.period),
    defect_rate: parseFloat((d.defect_rate_pct ?? 0).toFixed(2)),
  }));

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <h2 className="mb-4 text-sm font-semibold text-gray-800">Defect Rate Over Time</h2>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="defectGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: '#6b7280' }}
            tickLine={false}
            axisLine={{ stroke: '#e5e7eb' }}
          />
          <YAxis
            tickFormatter={(v: number) => `${v}%`}
            tick={{ fontSize: 11, fill: '#6b7280' }}
            tickLine={false}
            axisLine={false}
            width={42}
          />
          <Tooltip
            formatter={(value: number) => [`${value}%`, 'Defect Rate']}
            contentStyle={{
              borderRadius: '8px',
              border: '1px solid #e5e7eb',
              fontSize: '12px',
            }}
          />
          <Area
            type="monotone"
            dataKey="defect_rate"
            stroke="#ef4444"
            strokeWidth={2}
            fill="url(#defectGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
