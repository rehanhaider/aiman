import { twMerge } from "tailwind-merge";

// Accepted className inputs. Mirrors the subset of clsx we rely on: strings,
// numbers, conditional `cond && "class"`, and nested arrays. Keep this helper
// compatible with the className values used by generated shadcn components.
type ClassFn = (...args: never[]) => unknown;
export type ClassValue =
  | string
  | number
  | bigint
  | null
  | boolean
  | undefined
  | ClassFn
  | ClassValue[];

function flatten(value: ClassValue): string {
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "bigint")
    return String(value);
  if (Array.isArray(value)) return value.map(flatten).filter(Boolean).join(" ");
  return "";
}

/** Merge conditional class names and resolve Tailwind conflicts (last wins). */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(inputs.map(flatten).filter(Boolean).join(" "));
}
