import type { Defect } from '@/types/api';

interface DefectBadgeProps {
  defect: Defect;
}

export function DefectBadge({ defect }: DefectBadgeProps) {
  const { type, confidence } = defect;

  let colorClasses = '';
  if (confidence > 0.8) {
    colorClasses = 'bg-red-100 text-red-800 border-red-300';
  } else if (confidence > 0.5) {
    colorClasses = 'bg-yellow-100 text-yellow-800 border-yellow-300';
  } else {
    colorClasses = 'bg-green-100 text-green-800 border-green-300';
  }

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${colorClasses}`}
    >
      {type}
      <span className="opacity-75">({(confidence * 100).toFixed(0)}%)</span>
    </span>
  );
}
