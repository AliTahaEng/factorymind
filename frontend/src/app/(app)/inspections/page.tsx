import { InspectionTable } from '@/components/inspections/InspectionTable';

export default function InspectionsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-bold text-gray-900">Inspections</h1>
        <p className="mt-1 text-sm text-gray-500">
          Browse and search all recorded inspection events.
        </p>
      </div>
      <InspectionTable />
    </div>
  );
}
