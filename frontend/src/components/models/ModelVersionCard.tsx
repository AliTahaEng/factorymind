'use client';

import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { promoteModel, rollbackModel } from '@/lib/api';
import { useAuthStore } from '@/store/auth';
import type { ModelVersion } from '@/types/api';

interface ModelVersionCardProps {
  model: ModelVersion;
}

function StageBadge({ stage }: { stage: ModelVersion['stage'] }) {
  const styles: Record<ModelVersion['stage'], string> = {
    production: 'bg-green-100 text-green-800 border-green-300',
    staging: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    archived: 'bg-gray-100 text-gray-500 border-gray-300',
  };
  return (
    <span
      className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold capitalize ${styles[stage]}`}
    >
      {stage}
    </span>
  );
}

export function ModelVersionCard({ model }: ModelVersionCardProps) {
  const queryClient = useQueryClient();
  const user = useAuthStore((s) => s.user);
  const isAdmin = user?.role === 'admin';
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handlePromote() {
    setIsLoading(true);
    setError(null);
    try {
      await promoteModel(model.name);
      await queryClient.invalidateQueries({ queryKey: ['models'] });
    } catch {
      setError('Promote failed');
    } finally {
      setIsLoading(false);
    }
  }

  async function handleRollback() {
    setIsLoading(true);
    setError(null);
    try {
      await rollbackModel(model.name);
      await queryClient.invalidateQueries({ queryKey: ['models'] });
    } catch {
      setError('Rollback failed');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-4 rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="text-sm font-semibold text-gray-800">{model.name}</h3>
          <p className="mt-0.5 font-mono text-xs text-gray-500">v{model.version}</p>
        </div>
        <StageBadge stage={model.stage} />
      </div>

      {/* Metadata */}
      <div className="text-xs text-gray-500">
        Created: {new Date(model.created_at).toLocaleDateString()}
      </div>

      {/* Metrics */}
      {model.metrics && Object.keys(model.metrics).length > 0 && (
        <div className="rounded-lg bg-gray-50 p-3">
          <p className="mb-2 text-xs font-semibold uppercase text-gray-400">Metrics</p>
          <dl className="grid grid-cols-2 gap-x-4 gap-y-1">
            {Object.entries(model.metrics).map(([k, v]) => (
              <div key={k} className="flex justify-between">
                <dt className="text-xs text-gray-500">{k}</dt>
                <dd className="text-xs font-medium text-gray-700">{v}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      {/* Error */}
      {error && <p className="text-xs text-red-600">{error}</p>}

      {/* Actions (admin only) */}
      {isAdmin && (
        <div className="flex gap-2 pt-1">
          {model.stage !== 'production' && (
            <button
              onClick={handlePromote}
              disabled={isLoading}
              className="flex-1 rounded-lg bg-green-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-green-700 disabled:opacity-50"
            >
              Promote
            </button>
          )}
          {model.stage === 'production' && (
            <button
              onClick={handleRollback}
              disabled={isLoading}
              className="flex-1 rounded-lg bg-orange-500 px-3 py-1.5 text-xs font-semibold text-white hover:bg-orange-600 disabled:opacity-50"
            >
              Rollback
            </button>
          )}
        </div>
      )}
    </div>
  );
}
