import type { HTMLAttributes } from "react";

import { cn } from "../../lib/utils";

export function Badge({ className, ...props }: HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border border-slate-700 bg-slate-800 px-2 py-1 text-xs font-semibold text-slate-200",
        className,
      )}
      {...props}
    />
  );
}
