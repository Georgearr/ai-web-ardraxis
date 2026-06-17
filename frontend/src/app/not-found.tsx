import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Icon } from "@/components/shared/Icons"

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 px-4 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-muted">
        <Icon name="alert" className="text-muted-foreground" size={32} />
      </div>
      <h2 className="text-xl font-semibold">Halaman Tidak Ditemukan</h2>
      <p className="max-w-md text-sm text-muted-foreground">
        Halaman yang Anda cari tidak tersedia.
      </p>
      <Button asChild>
        <Link href="/">Kembali ke Beranda</Link>
      </Button>
    </div>
  )
}
