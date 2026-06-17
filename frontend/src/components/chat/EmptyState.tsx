import { Icon } from "@/components/shared/Icons"

interface EmptyStateProps {
  onSuggestionClick: (suggestion: string) => void
  suggestions: string[]
}

export function EmptyState({ onSuggestionClick, suggestions }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center px-4 py-12 text-center animate-fade-in">
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
        <Icon name="sparkles" className="text-primary" size={32} />
      </div>
      <h2 className="mb-1 text-xl font-semibold">Halo! Ada yang bisa dibantu?</h2>
      <p className="mb-8 max-w-md text-sm text-muted-foreground">
        Tanyakan tentang OSIS SMA Ignatius Global School &mdash; anggota, struktur, event, dan
        informasi resmi lainnya.
      </p>
      <div className="grid w-full max-w-lg grid-cols-1 gap-2 sm:grid-cols-2">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onSuggestionClick(suggestion)}
            className="group flex items-center gap-2 rounded-lg border bg-card px-4 py-3 text-left text-sm shadow-sm transition-all hover:bg-accent hover:shadow-md"
          >
            <Icon
              name="lightbulb"
              className="shrink-0 text-muted-foreground group-hover:text-primary"
              size={16}
            />
            <span className="line-clamp-2">{suggestion}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
