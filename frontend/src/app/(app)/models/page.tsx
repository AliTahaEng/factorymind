'use client';

import { useQuery } from '@tanstack/react-query';
import { getModels } from '@/lib/api';
import { ModelVersionCard } from '@/components/models/ModelVersionCard';

export default function ModelsPage() {
  const { data: models, isLoading, isError } = useQuery({
    queryKey: ['models'],
    queryFn: getModels,
    staleTime: 60_000,
  });

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-bold text-gray-900">Model Versions</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage and promote ML model versions.
        </p>
      </div>

      {isLoading && (
        <div className="flex h-32 items-center justify-center text-sm text-gray-400">
          Loading models…
        </div>
      )}

      {isError && (
        <div className="flex h-32 items-center justify-center rounded-xl border border-red-200 bg-red-50 text-sm text-red-600">
          Failed to load models.
        </div>
      )}

      {models && models.length === 0 && (
        <div className="flex h-32 items-center justify-center rounded-xl border border-gray-200 bg-white text-sm text-gray-400">
          No models registered yet.
        </div>
      )}

      {models && models.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {models.map((model) => (
            <ModelVersionCard key={`${model.name}-${model.version}`} model={model} />
          ))}
        </div>
      )}
    </div>
  );
}
