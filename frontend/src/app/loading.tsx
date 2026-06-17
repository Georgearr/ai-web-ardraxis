import { Skeleton } from "@/components/ui/skeleton"

export default function Loading() {
  return (
    <div className="mx-auto flex h-[calc(100vh-8rem)] max-w-4xl flex-col rounded-xl border bg-card p-6 shadow-sm md:my-4 md:h-[calc(100vh-10rem)]">
      <div className="flex flex-col gap-4">
        <div className="flex items-center gap-3">
          <Skeleton className="h-8 w-8 rounded-full" />
          <Skeleton className="h-16 flex-1 rounded-2xl" />
        </div>
        <div className="flex flex-row-reverse items-center gap-3">
          <Skeleton className="h-8 w-8 rounded-full" />
          <Skeleton className="h-16 flex-1 rounded-2xl" />
        </div>
      </div>
    </div>
  )
}
