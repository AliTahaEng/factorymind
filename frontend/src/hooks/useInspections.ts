'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getInspections } from '@/lib/api';

export function useInspections(initialPage = 1, pageSize = 20) {
  const [page, setPage] = useState(initialPage);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['inspections', page, pageSize],
    queryFn: () => getInspections(page, pageSize),
    staleTime: 30_000,
  });

  return {
    inspections: data?.items ?? [],
    total: data?.total ?? 0,
    page,
    setPage,
    isLoading,
    isError,
    error,
  };
}
