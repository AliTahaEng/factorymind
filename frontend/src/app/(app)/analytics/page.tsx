import { DefectRateChart } from '@/components/analytics/DefectRateChart';
import { ModelPerformanceTable } from '@/components/analytics/ModelPerformanceTable';

export default function AnalyticsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-bold text-gray-900">Analytics</h1>
        <p className="mt-1 text-sm text-gray-500">
          Defect trends and model performance metrics.
        </p>
      </div>
      <DefectRateChart />
      <ModelPerformanceTable />
    </div>
  );
}
