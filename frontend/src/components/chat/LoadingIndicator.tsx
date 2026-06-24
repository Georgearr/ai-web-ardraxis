export function LoadingIndicator() {
  return (
    <div className="flex w-full gap-3 px-4 pb-4 animate-fade-in">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[rgba(255,255,255,0.12)] bg-[rgba(0,0,0,0.25)] backdrop-blur-[6px]">
        <span className="text-sm font-black text-transparent bg-gradient-to-br from-white to-[#b2dfdb] bg-clip-text">
          D
        </span>
      </div>
      <div className="flex items-center gap-1 rounded-2xl rounded-tl-md glass-card px-4 py-3">
        <span className="h-2 w-2 animate-pulse-dot rounded-full bg-[#b2dfdb]/60 [animation-delay:0ms]" />
        <span className="h-2 w-2 animate-pulse-dot rounded-full bg-[#b2dfdb]/60 [animation-delay:200ms]" />
        <span className="h-2 w-2 animate-pulse-dot rounded-full bg-[#b2dfdb]/60 [animation-delay:400ms]" />
      </div>
    </div>
  )
}
