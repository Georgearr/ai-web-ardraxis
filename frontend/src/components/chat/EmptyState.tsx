import { Icon } from "@/components/shared/Icons"

interface EmptyStateProps {
  onSuggestionClick: (suggestion: string) => void
  suggestions: string[]
}

export function EmptyState({ onSuggestionClick, suggestions }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center px-4 py-4 text-center animate-fade-in">
      <div className="mb-3 flex h-16 w-16 items-center justify-center rounded-2xl bg-[rgba(255,255,255,0.06)] border border-[rgba(255,255,255,0.12)] backdrop-blur-[6px] shadow-[0_10px_30px_rgba(0,0,0,0.3)]">
        <span className="text-3xl font-black text-transparent bg-gradient-to-br from-white to-[#b2dfdb] bg-clip-text md:text-4xl">
          D
        </span>
      </div>
      <h2 className="mb-1 text-lg font-black tracking-[0.5px] text-white drop-shadow-[0_2px_10px_rgba(0,0,0,0.3)] md:text-xl">
        DRAX
      </h2>
      <p className="mb-1 text-[11px] font-extrabold tracking-[0.3px] text-[#96cccd] uppercase md:text-xs">
        Digital Resource Assistant of ARDRAXIS
      </p>
      <p className="mb-4 max-w-md text-sm font-light tracking-[1px] text-[#b2dfdb] leading-relaxed">
        Empowering Information, Igniting Innovation.
        <br />
        Tanyakan tentang OSIS SMA Ignatius Global School.
      </p>
      <div className="grid w-full max-w-lg grid-cols-1 gap-2 sm:grid-cols-2">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onSuggestionClick(suggestion)}
            className="group flex items-center gap-2 rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(0,0,0,0.25)] backdrop-blur-[6px] px-4 py-3 text-left text-sm text-white shadow-[0_10px_30px_rgba(0,0,0,0.3)] transition-all duration-250 hover:-translate-y-1 hover:border-[rgba(255,255,255,0.22)] hover:bg-[rgba(0,0,0,0.32)] hover:shadow-[0_20px_40px_rgba(0,0,0,0.5)]"
          >
            <Icon
              name="lightbulb"
              className="shrink-0 text-[#b2dfdb] group-hover:text-[#96cccd]"
              size={16}
            />
            <span className="line-clamp-2 text-white/90">{suggestion}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
