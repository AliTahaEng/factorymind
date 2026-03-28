'use client';

import { useRouter } from 'next/navigation';
import { useInspections } from '@/hooks/useInspections';

export function InspectionTable() {
  const router = useRouter();
  const { inspections, total, page, setPage, isLoading } = useInspections(1, 20);
  const pageSize = 20;
  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="flex flex-col gap-4">
      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 text-left">
                {['ID', 'Camera', 'Timestamp', 'Defect Prob.', 'Status'].map((col) => (
                  <th
                    key={col}
                    className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-gray-500"
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="py-10 text-center text-sm text-gray-400">
                    Loading inspections…
                  </td>
                </tr>
              ) : inspections.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-10 text-center text-sm text-gray-400">
                    No inspections found.
                  </td>
                </tr>
              ) : (
                inspections.map((inspection) => (
                  <tr
                    key={inspection.inspection_id}
                    className="cursor-pointer hover:bg-blue-50 transition-colors"
                    onClick={() => router.push(`/inspections/${inspection.inspection_id}`)}
                  >
                    <td className="px-4 py-3 font-mono text-xs text-gray-500">
                      {inspection.inspection_id.slice(0, 8)}…
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">{inspection.camera_id}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-600">
                      {new Date(inspection.inspected_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-20 rounded-full bg-gray-200">
                          <div
                            className={`h-1.5 rounded-full ${
                              inspection.defect_score > 0.5
                                ? 'bg-red-500'
                                : 'bg-green-500'
                            }`}
                            style={{
                              width: `${Math.round(inspection.defect_score * 100)}%`,
                            }}
                          />
                        </div>
                        <span className="text-xs text-gray-600">
                          {(inspection.defect_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      {inspection.is_defective ? (
                        <span className="rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-semibold text-red-700">
                          Defect
                        </span>
                      ) : (
                        <span className="rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-semibold text-green-700">
                          OK
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>
            Page {page} of {totalPages} ({total} total)
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-medium hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Previous
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-medium hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
