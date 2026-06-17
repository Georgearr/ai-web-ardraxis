export function LoadingIndicator() {
  return (
    <div className="flex w-full gap-3 px-4 pb-4 animate-fade-in">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted">
        <span className="text-sm font-medium text-muted-foreground">D</span>
      </div>
      <div className="flex items-center gap-1 rounded-2xl rounded-tl-md bg-muted px-4 py-3">
        <span className="h-2 w-2 animate-pulse-dot rounded-full bg-muted-foreground/60 [animation-delay:0ms]" />
        <span className="h-2 w-2 animate-pulse-dot rounded-full bg-muted-foreground/60 [animation-delay:200ms]" />
        <span className="h-2 w-2 animate-pulse-dot rounded-full bg-muted-foreground/60 [animation-delay:400ms]" />
      </div>
    </div>
  )
}
