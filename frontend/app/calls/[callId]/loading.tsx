export default function Loading() {
  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl">
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-2">
          <div className="animate-spin h-8 w-8 border-4 border-prefect-blue-500 border-t-transparent rounded-full mx-auto" />
          <p className="text-sm text-muted-foreground">
            Loading call analysis...
          </p>
        </div>
      </div>
    </div>
  );
}
