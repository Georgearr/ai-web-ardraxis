"use client"

import { Button } from "@/components/ui/button"
import { Icon } from "@/components/shared/Icons"

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 px-4 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-destructive/10">
        <Icon name="alert" className="text-destructive" size={32} />
      </div>
      <h2 className="text-xl font-semibold">Terjadi Kesalahan</h2>
      <p className="max-w-md text-sm text-muted-foreground">
        Maaf, terjadi kesalahan yang tidak terduga. Silakan coba lagi.
      </p>
      <Button onClick={reset}>Coba Lagi</Button>
    </div>
  )
}
