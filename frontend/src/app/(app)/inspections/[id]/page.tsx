'use client';

import { useParams, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { getInspection } from '@/lib/api';

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5">
      <dt className="text-xs font-medium uppercase tracking-wide text-gray-400">{label}</dt>
      <dd className="text-sm text-gray-800">{value}</dd>
    </div>
  );
}

export default function InspectionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const { data: inspection, isLoading, isError } = useQuery({
    queryKey: ['inspection', id],
    queryFn: () => getInspection(id),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-gray-400">
        Loading inspection…
      </div>
    );
  }

  if (isError || !inspection) {
    return (
      <div className="flex h-64 flex-col items-center justify-center gap-3 text-sm text-red-600">
        <span>Failed to load inspection.</span>
        <button
          onClick={() => router.back()}
          className="text-xs text-gray-500 underline hover:text-gray-800"
        >
          Go back
        </button>
      </div>
    );
  }

  const pct = Math.round(inspection.defect_score * 100);

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-800"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        <h1 className="text-xl font-bold text-gray-900">Inspection Detail</h1>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Core details */}
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="mb-5 text-sm font-semibold text-gray-800">Details</h2>
          <dl className="grid grid-cols-2 gap-x-6 gap-y-4">
            <Field label="Inspection ID" value={<span className="font-mono text-xs">{inspection.inspection_id}</span>} />
            <Field label="Image ID" value={<span className="font-mono text-xs">{inspection.image_id}</span>} />
            <Field label="Camera" value={inspection.camera_id} />
            <Field
              label="Inspected At"
              value={new Date(inspection.inspected_at).toLocaleString()}
            />
            <Field label="Model Version" value={inspection.model_version ?? '—'} />
            <Field label="Processing Time" value={`${inspection.processing_time_ms} ms`} />
            <Field label="Anomaly Score" value={(inspection.anomaly_score * 100).toFixed(1) + '%'} />
            <Field label="Classification" value={inspection.classification_label ?? '—'} />
            <Field
              label="Status"
              value={
                inspection.is_defective ? (
                  <span className="rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-semibold text-red-700">
                    Defect Detected
                  </span>
                ) : (
                  <span className="rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-semibold text-green-700">
                    OK
                  </span>
                )
              }
            />
          </dl>
        </div>

        {/* Defect score gauge */}
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="mb-5 text-sm font-semibold text-gray-800">Defect Score</h2>
          <div className="flex flex-col items-center gap-4">
            <div className="relative flex h-36 w-36 items-center justify-center">
              <svg className="absolute inset-0" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="50" fill="none" stroke="#f3f4f6" strokeWidth="12" />
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  fill="none"
                  stroke={pct > 50 ? '#ef4444' : '#22c55e'}
                  strokeWidth="12"
                  strokeDasharray={`${(pct / 100) * 314} 314`}
                  strokeLinecap="round"
                  transform="rotate(-90 60 60)"
                />
              </svg>
              <span className={`text-3xl font-bold ${pct > 50 ? 'text-red-600' : 'text-green-600'}`}>
                {pct}%
              </span>
            </div>
            <p className="text-sm text-gray-500">
              {pct > 50 ? 'High defect probability' : 'Low defect probability'}
            </p>
          </div>
        </div>
      </div>

      {/* Bounding boxes / detected defects */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-sm font-semibold text-gray-800">
          Detected Bounding Boxes ({inspection.bounding_boxes.length})
        </h2>
        {inspection.bounding_boxes.length === 0 ? (
          <p className="text-sm text-gray-400">No bounding boxes detected.</p>
        ) : (
          <div className="flex flex-col gap-3">
            {inspection.bounding_boxes.map((bbox, i) => (
              <div
                key={i}
                className="flex items-center justify-between rounded-lg bg-gray-50 px-4 py-3"
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${
                      bbox.confidence > 0.8
                        ? 'border-red-300 bg-red-100 text-red-800'
                        : bbox.confidence > 0.5
                        ? 'border-yellow-300 bg-yellow-100 text-yellow-800'
                        : 'border-green-300 bg-green-100 text-green-800'
                    }`}
                  >
                    {bbox.label}
                    <span className="opacity-75">({(bbox.confidence * 100).toFixed(0)}%)</span>
                  </span>
                </div>
                <span className="font-mono text-xs text-gray-400">
                  x:{bbox.x.toFixed(0)} y:{bbox.y.toFixed(0)} w:{bbox.w.toFixed(0)} h:{bbox.h.toFixed(0)}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
