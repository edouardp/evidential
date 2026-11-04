/** Shared data-only contracts for the gradually checked JavaScript boundary. */
export interface CsvColumn { name: string; title?: string | null }
export interface ScaleColumn {
  scale?: {
    domain?: [number | null, number | null];
    transform?: string;
    include_zero?: boolean;
  };
  encodings?: Array<{
    kind: string;
    fit_to_data?: boolean;
    center?: boolean;
    side?: string;
    diverge_at?: string;
  }>;
}
export interface MarkDomain {
  lo: number;
  hi: number;
  span: number;
  transform?: string;
}
