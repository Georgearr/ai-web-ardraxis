import type { LucideIcon } from "lucide-react"
import {
  Bot,
  Send,
  Sparkles,
  User,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
  MessageSquare,
  Lightbulb,
  ArrowRight,
  Loader2,
  RefreshCw,
} from "lucide-react"

export type IconName =
  | "bot"
  | "send"
  | "sparkles"
  | "user"
  | "alert"
  | "chevron-left"
  | "chevron-right"
  | "menu"
  | "x"
  | "chat"
  | "lightbulb"
  | "arrow-right"
  | "spinner"
  | "refresh"

const iconMap: Record<IconName, LucideIcon> = {
  bot: Bot,
  send: Send,
  sparkles: Sparkles,
  user: User,
  alert: AlertCircle,
  "chevron-left": ChevronLeft,
  "chevron-right": ChevronRight,
  menu: Menu,
  x: X,
  chat: MessageSquare,
  lightbulb: Lightbulb,
  "arrow-right": ArrowRight,
  spinner: Loader2,
  refresh: RefreshCw,
}

interface IconProps {
  name: IconName
  className?: string
  size?: number
}

export function Icon({ name, className, size = 16 }: IconProps) {
  const LucideIcon = iconMap[name]
  if (!LucideIcon) return null
  return <LucideIcon className={className} size={size} />
}
