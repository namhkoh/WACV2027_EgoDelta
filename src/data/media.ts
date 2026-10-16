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
    caption: "Harvesting with the EgoDelta learned policy (2× speed).",
  },
  {
    tab: "deleafing",
    src: "videos/teaser_deleafing.mp4",
    // Three portrait trials side by side.
    aspect: "1238 / 720",
    caption: "Deleafing with the EgoDelta learned policy, three trials (2× speed).",
  },
];

function demo(id: string, tab: string, group: string, title: string): Clip {
  return {
    tab,
    group,
    title,
    panels: [
      { label: "Egocentric demonstration", src: `videos/${id}_demo.mp4`, aspect: EGO },
      { label: "Pre-action 2DGS", src: `videos/${id}_pre.mp4`, aspect: EGO },
      { label: "Post-action 2DGS", src: `videos/${id}_post.mp4`, aspect: EGO },
      { label: "Removal score + attachment target", src: `videos/${id}_target.mp4`, aspect: EGO, ours: true },
    ],
  };
}

export const demonstrations: Clip[] = [
  demo("harvest1", "tomato #1", "Harvesting", "Harvesting — tomato #1"),
  demo("harvest2", "tomato #2", "Harvesting", "Harvesting — tomato #2"),
  demo("deleaf1", "leaf #1", "Deleafing", "Deleafing — leaf #1"),
  demo("deleaf2", "leaf #2", "Deleafing", "Deleafing — leaf #2"),
];

// Learned-policy runs filmed with a phone and sped up 2x: harvesting is
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
