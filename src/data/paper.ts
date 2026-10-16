// Everything shown in the page header, abstract and citation lives here.
// Fill in the TODOs once the camera-ready links are final.

export type Author = {
  name: string;
  url?: string;
  /** 1-based indices into `affiliations`. */
  affiliations: number[];
  /** Extra marks such as "*" for equal contribution; explained in `notes`. */
  marks?: string[];
};

export type Link = {
  label: string;
  /** Leave undefined to show the button as "soon" (disabled). */
  url?: string;
};

export const paper = {
  name: "EgoDelta",
  title:
    "From Egocentric Scene Change to 3D Attachment Targets for Agricultural Manipulation",
  venue: "WACV 2027",
  track: "Applications Track",
  summary:
    "EgoDelta turns the scene change left behind by a human removal demonstration into 3D attachment targets and robot-ready trajectories for harvesting and deleafing.",

  authors: [
    { name: "Nam Ho Koh", affiliations: [1], marks: ["*"] },
    { name: "Junyoung Jang", affiliations: [2], marks: ["*"] },
    { name: "Chaeyoung Oh", affiliations: [1] },
    { name: "Changwoo Yoo", affiliations: [1] },
    { name: "Jongho Lee", affiliations: [3] },
    { name: "Kee-Eung Kim", affiliations: [1] },
  ] as Author[],
  affiliations: [
    "Kim Jaechul Graduate School of AI, KAIST, Daejeon, Republic of Korea",
    "KT Corporation, Seoul, Republic of Korea",
    "Daedong AI Lab",
  ],
  // Explains the marks used on authors.
  notes: [{ mark: "*", text: "Equal contribution" }],

  // TODO: add URLs as they become available; buttons without a URL render as "soon".
  links: [
    { label: "Paper" },
    { label: "arXiv" },
    { label: "Code" },
    { label: "Video" },
  ] as Link[],

  abstract: `Agricultural tasks such as fruit harvesting and deleafing require removing components at their attachment targets: the 3D locations where they connect to the plant. These targets are often occluded and need not coincide with component centers. Egocentric video captures human removal demonstrations without requiring robot hardware, but provides neither 3D target labels nor robot-executable motion. The persistent scene change produced by a completed removal nevertheless provides spatial evidence of both the removed component and its former connection. We introduce EgoDelta, an integrated pipeline that recovers attachment targets from this evidence without attachment-target annotations and converts the demonstrations into robot-specific supervision. EgoDelta reconstructs the pre- and post-action scene states with 2D Gaussian Splatting and scores each pre-action surface using geometric and appearance changes weighted by observation reliability. It uses these scores to localize the removed component and retains them together with evidence from nearby remaining plant surfaces to recover the former connection. Recovered targets supervise an attachment-target predictor, while target-anchored robot-specific trajectories adapted from tracked hand motion supervise a target-conditioned policy. Across 160 targets from 60 interventions, EgoDelta achieves 92.83% F1 at a 3 cm matching tolerance. Across 180 physical robot trials, executing EgoDelta-generated trajectories without policy learning succeeds in 100% of trials, compared with 43.3% for direct human-motion retargeting. The learned policy succeeds in 91.7% of trials.`,

  // The four stages of Figure 1.
  method: [
    {
      title: "Egocentric pre/post demonstration",
      text: "A worker wearing Project Aria glasses records one continuous removal. Aria MPS provides camera poses and semi-dense scene points; frames sampled before and after the action form two view sets that need not share viewpoints.",
    },
    {
      title: "2DGS reconstruction",
      text: "The plant is reconstructed independently before and after removal with 2D Gaussian Splatting in a common scene frame, so geometry removed by the action is absent from the post-action model.",
    },
    {
      title: "Extract attachment target",
      text: "Each pre-action surface primitive is scored by its geometric and appearance mismatch, weighted by how reliably it was observed. Continuous scores and remaining-surface evidence then locate the former connection.",
    },
    {
      title: "Robot trajectory generation",
      text: "The target anchors the robot's contact point while tracked hand motion supplies approach and manipulation directions, yielding feasible trajectories that also supervise a target-conditioned policy.",
    },
  ],

  bibtex: {
    key: "egodelta2027",
    booktitle:
      "Proceedings of the IEEE/CVF Winter Conference on Applications of Computer Vision (WACV)",
    year: 2027,
  },
};

/** "First Middle Last" -> "Last, First Middle", joined the way BibTeX expects. */
function bibtexAuthors(authors: Author[]): string {
  return authors
    .map(({ name }) => {
      const parts = name.trim().split(/\s+/);
      const last = parts.pop();
      return parts.length ? `${last}, ${parts.join(" ")}` : `${last}`;
    })
    .join(" and ");
}

export const bibtex = `@inproceedings{${paper.bibtex.key},
  title     = {{${paper.name}}: ${paper.title}},
  author    = {${bibtexAuthors(paper.authors)}},
  booktitle = {${paper.bibtex.booktitle}},
  year      = {${paper.bibtex.year}}
}`;
