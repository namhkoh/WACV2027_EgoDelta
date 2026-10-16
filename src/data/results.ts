// Numbers transcribed from the paper's Tables 1-5. The bar charts and the
// trial grid read from these tables, so each number lives in exactly one place.

export type Column = {
  label: string;
  /** Which direction is better; used to bold the best value per column. */
  better: "up" | "down";
  decimals: number;
  /** For success counts: render as `value/outOf`. */
  outOf?: number;
};

export type Row = {
  method: string;
  values: number[];
  ours?: boolean;
  /** Draw a divider above this row (separates the full configuration). */
  divider?: boolean;
  /** Italic section label shown above this row. */
  section?: string;
};

export type ResultTable = {
  id: string;
  tab: string;
  title: string;
  caption: string;
  /** Optional header row spanning several columns, e.g. interaction settings. */
  groups?: { label: string; span: number }[];
  columns: Column[];
  rows: Row[];
};

const iouF1 = (): Column[] =>
  ["Harvesting", "Deleafing", "Overall"].flatMap(() => [
    { label: "IoU (%)", better: "up", decimals: 1 },
    { label: "F1 (%)", better: "up", decimals: 1 },
  ]);

const settingsGroups = [
  { label: "Harvesting", span: 2 },
  { label: "Deleafing", span: 2 },
  { label: "Overall", span: 2 },
];

const recoveryColumns: Column[] = [
  { label: "Harvesting F1@3 cm (%)", better: "up", decimals: 2 },
  { label: "Deleafing F1@3 cm (%)", better: "up", decimals: 2 },
  { label: "Overall F1@3 cm (%)", better: "up", decimals: 2 },
  { label: "Median error (cm)", better: "down", decimals: 2 },
];

export const localization: ResultTable = {
  id: "t1",
  tab: "2D localization",
  title: "Table 1 · 2D removed-component localization",
  caption:
    "All methods are evaluated against the same 720 reference masks; the point-cloud residual receives only MPS semi-dense point clouds.",
  groups: settingsGroups,
  columns: iouF1(),
  rows: [
    { method: "Point-cloud residual", values: [29.6, 43.1, 51.3, 67.6, 40.4, 55.4] },
    { method: "YOLOE-Seg", values: [26.2, 40.9, 6.1, 11.0, 16.1, 26.0] },
    { method: "SAM 3", values: [28.8, 43.7, 30.3, 46.0, 29.6, 44.8] },
    { method: "3DGS-CD", values: [27.1, 32.0, 4.9, 8.2, 16.0, 20.1] },
    { method: "GS-DIFF", values: [11.2, 19.7, 34.0, 50.2, 22.6, 35.0] },
    { method: "MV3DCD", values: [33.1, 45.5, 36.7, 50.6, 34.9, 48.0] },
    { method: "EgoDelta (ours)", values: [62.4, 75.8, 71.5, 83.2, 67.0, 79.5], ours: true, divider: true },
  ],
};

export const localizationAblation: ResultTable = {
  id: "t2",
  tab: "Localization ablation",
  title: "Table 2 · Ablation of removed-component localization",
  caption:
    "Each variant changes one scene-comparison choice; all values are percentages under the 720-mask protocol of Table 1.",
  groups: settingsGroups,
  columns: iouF1(),
  rows: [
    { method: "Appearance only", values: [60.0, 71.9, 68.8, 81.2, 64.4, 76.6] },
    { method: "Geometry only", values: [49.3, 59.8, 71.2, 82.9, 60.2, 71.4] },
    { method: "No observability weight", values: [49.6, 64.6, 70.7, 82.6, 60.2, 73.6] },
    { method: "No shared-view filter", values: [62.6, 75.9, 70.7, 82.7, 66.7, 79.2] },
    { method: "Fixed-radius match", values: [52.2, 63.0, 70.9, 82.8, 61.5, 72.9] },
    { method: "EgoDelta (full)", values: [62.4, 75.8, 71.5, 83.2, 67.0, 79.5], ours: true, divider: true },
  ],
};

export const recovery: ResultTable = {
  id: "t3",
  tab: "3D target recovery",
  title: "Table 3 · 3D attachment-target recovery",
  caption:
    "Binary-input rows use the same fixed recovery procedure within each interaction setting; full EgoDelta retains continuous removal scores and remaining-surface evidence. Median error uses matched predictions only; F1 also penalizes unmatched predictions and targets.",
  columns: recoveryColumns,
  rows: [
    { method: "Point-cloud residual + binary recovery", values: [37.1, 24.38, 26.32, 1.79], section: "Binary removed-component input" },
    { method: "YOLOE-Seg + binary recovery", values: [14.29, 14.07, 14.15, 2.03] },
    { method: "SAM 3 + binary recovery", values: [13.42, 3.99, 5.07, 1.98] },
    { method: "3DGS-CD + binary recovery", values: [11.57, 6.48, 8.15, 2.38] },
    { method: "GS-DIFF + binary recovery", values: [7.95, 21.61, 16.5, 1.88] },
    { method: "MV3DCD + binary recovery", values: [1.73, 6.13, 4.15, 1.89] },
    { method: "EgoDelta + binary recovery", values: [35.05, 27.56, 28.71, 1.84] },
    { method: "EgoDelta (full)", values: [94.44, 92.02, 92.83, 1.17], ours: true, divider: true, section: "Continuous scene-change evidence" },
  ],
};

export const selection: ResultTable = {
  id: "t4",
  tab: "Target selection",
  title: "Table 4 · Attachment-target selection on fixed EgoDelta proposals",
  caption:
    "Rules share proposals and pre-action geometry; scene-change scores are used when required.",
  columns: recoveryColumns,
  rows: [
    { method: "Component centroid", values: [76.64, 0.0, 25.62, 2.31] },
    { method: "Score-weighted centroid", values: [76.64, 0.0, 25.62, 2.33] },
    { method: "Closest to remaining surface", values: [52.34, 73.24, 66.25, 1.27] },
    { method: "PCA endpoint", values: [3.74, 78.87, 53.75, 1.35] },
    { method: "EgoDelta selection", values: [94.44, 92.02, 92.83, 1.17], ours: true, divider: true },
  ],
};

export const robot: ResultTable = {
  id: "t5",
  tab: "Robot execution",
  title: "Table 5 · Robot execution on held-out arrangements",
  caption:
    "Successful trials out of 30 per interaction setting; any rejection or interruption counts as a failure.",
  columns: [
    { label: "Harvesting", better: "up", decimals: 0, outOf: 30 },
    { label: "Deleafing", better: "up", decimals: 0, outOf: 30 },
  ],
  rows: [
    { method: "Direct human-motion retargeting", values: [12, 14] },
    { method: "EgoDelta trajectories (no policy learning)", values: [30, 30], ours: true },
    { method: "EgoDelta learned policy", values: [28, 27], ours: true },
  ],
};

export const tables = [localization, localizationAblation, recovery, selection, robot];

function row(table: ResultTable, method: string): Row {
  const found = table.rows.find((r) => r.method === method);
  if (!found) throw new Error(`No row "${method}" in ${table.id}`);
  return found;
}

export type Bar = {
  /** One string per line of the axis label. */
  label: string[];
  value: number;
  ours?: boolean;
  /** Shown in the hover tooltip. */
  detail: string;
};

export type Chart = {
  title: string;
  note: string;
  unit: string;
  decimals: number;
  max: number;
  bars: Bar[];
};

function f1Bar(table: ResultTable, method: string, label: string[], ours = false): Bar {
  const v = row(table, method).values;
  return {
    label,
    value: v[5],
    ours,
    detail: `harvesting ${v[1].toFixed(1)} · deleafing ${v[3].toFixed(1)}`,
  };
}

function recoveryBar(method: string, label: string[], ours = false): Bar {
  const v = row(recovery, method).values;
  return {
    label,
    value: v[2],
    ours,
    detail: `harvesting ${v[0].toFixed(2)} · deleafing ${v[1].toFixed(2)} · median ${v[3].toFixed(2)} cm`,
  };
}

function successBar(method: string, label: string[], ours = false): Bar {
  const [h, d] = row(robot, method).values;
  const total = robot.columns.reduce((n, c) => n + (c.outOf ?? 0), 0);
  return {
    label,
    value: ((h + d) / total) * 100,
    ours,
    detail: `${h + d}/${total} trials · harvesting ${h}/30 · deleafing ${d}/30`,
  };
}

export const charts: Chart[] = [
  {
    title: "Removed-component localization",
    note: "overall F1 (%) ↑ · 720 reference masks",
    unit: "%",
    decimals: 1,
    max: 100,
    bars: [
      f1Bar(localization, "MV3DCD", ["MV3DCD"]),
      f1Bar(localization, "Point-cloud residual", ["Point-cloud", "residual"]),
      f1Bar(localization, "EgoDelta (ours)", ["EgoDelta", "(ours)"], true),
    ],
  },
  {
    title: "3D attachment-target recovery",
    note: "overall F1@3 cm (%) ↑ · 160 targets",
    unit: "%",
    decimals: 1,
    max: 100,
    bars: [
      recoveryBar("Point-cloud residual + binary recovery", ["Point-cloud", "residual"]),
      recoveryBar("EgoDelta + binary recovery", ["EgoDelta", "binary input"]),
      recoveryBar("EgoDelta (full)", ["EgoDelta", "(ours)"], true),
    ],
  },
  {
    title: "Physical robot execution",
    note: "success rate (%) ↑ · 60 trials per mode",
    unit: "%",
    decimals: 1,
    max: 100,
    bars: [
      successBar("Direct human-motion retargeting", ["Human-motion", "retargeting"]),
      successBar("EgoDelta learned policy", ["EgoDelta", "learned policy"], true),
      successBar("EgoDelta trajectories (no policy learning)", ["EgoDelta", "trajectories"], true),
    ],
  },
];

/** Per-mode success counts for the trial grid, straight from Table 5. */
export const trials = robot.rows.map((r) => ({
  mode: r.method,
  ours: r.ours ?? false,
  settings: robot.columns.map((c, i) => ({
    label: c.label,
    successes: r.values[i],
    total: c.outOf ?? 0,
  })),
}));
