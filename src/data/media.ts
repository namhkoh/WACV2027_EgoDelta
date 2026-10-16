// Video slots on the page. Each `src` is a path under public/. Until a file
// exists at that path the page shows a "video coming soon" placeholder in its
// place, so adding a video only takes copying it to the expected filename.
// Add, remove or rename clips here; panels marked `ours` get the accent border.

export type Panel = {
  label: string;
  src: string;
  ours?: boolean;
  /** Aspect ratio of the placeholder box; real videos keep their own. */
  aspect?: string;
};

export type Clip = {
  /** Tab label. */
  tab: string;
  /** Tabs sharing a group are shown on one labelled row. */
  group?: string;
  title: string;
  panels: Panel[];
};

// Project Aria RGB frames are square fisheye images.
const EGO = "1 / 1";
const WIDE = "16 / 9";
const TALL = "9 / 16";

export const teaserVideos: { tab: string; src: string; caption: string; aspect: string }[] = [
  {
    tab: "harvesting",
    src: "videos/teaser_harvesting.mp4",
    aspect: WIDE,
    caption: "Harvesting with the EgoDelta learned policy.",
  },
  {
    tab: "deleafing",
    src: "videos/teaser_deleafing.mp4",
    // Three portrait trials side by side.
    aspect: "1238 / 720",
    caption: "Deleafing with the EgoDelta learned policy, three trials.",
  },
];

// One sample deleafing removal, left to right: the Aria demonstration, an illustrative animation of the
// pipeline built from its frames (tools/demo-film), and the robot performing the task.
export const demonstration: Panel[] = [
  { label: "Egocentric demonstration", src: "videos/demo_egocentric.mp4", aspect: EGO },
  { label: "EgoDelta pipeline (illustration)", src: "videos/demo_pipeline.mp4", aspect: EGO, ours: true },
  { label: "Robot execution", src: "videos/demo_robot.mp4", aspect: EGO },
];

// Learned-policy runs filmed with a phone and sped up 3x: harvesting is
// landscape, deleafing portrait.
function policy(task: string, n: number, aspect: string): Panel[] {
  return Array.from({ length: n }, (_, k) => ({
    label: `Trial ${k + 1}`,
    src: `videos/robot_${task}${k + 1}_policy.mp4`,
    aspect,
  }));
}

export const robotTrials: Clip[] = [
  { tab: "harvesting", title: "Harvesting", panels: policy("harvest", 2, WIDE) },
  { tab: "deleafing", title: "Deleafing", panels: policy("deleaf", 3, TALL) },
];
