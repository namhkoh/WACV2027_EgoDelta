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

export const teaserVideos: { tab: string; src: string; caption: string }[] = [
  {
    tab: "harvesting",
    src: "videos/teaser_harvesting.mp4",
    caption: "Harvesting: egocentric demonstration and EgoDelta robot execution.",
  },
  {
    tab: "deleafing",
    src: "videos/teaser_deleafing.mp4",
    caption: "Deleafing: egocentric demonstration and EgoDelta robot execution.",
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

function trial(id: string, tab: string, group: string, title: string): Clip {
  return {
    tab,
    group,
    title,
    panels: [
      { label: "Human-motion retargeting", src: `videos/robot_${id}_retarget.mp4`, aspect: WIDE },
      { label: "EgoDelta trajectory (ours)", src: `videos/robot_${id}_trajectory.mp4`, aspect: WIDE, ours: true },
      { label: "EgoDelta learned policy (ours)", src: `videos/robot_${id}_policy.mp4`, aspect: WIDE, ours: true },
    ],
  };
}

export const robotTrials: Clip[] = [
  trial("harvest1", "trial #1", "Harvesting", "Harvesting — trial #1"),
  trial("harvest2", "trial #2", "Harvesting", "Harvesting — trial #2"),
  trial("deleaf1", "trial #1", "Deleafing", "Deleafing — trial #1"),
  trial("deleaf2", "trial #2", "Deleafing", "Deleafing — trial #2"),
];
