import React from "react";
import { CalculateMetadataFunction, Composition } from "remotion";
import { buildShots, ExampleProps, Project } from "./kit";
import { PromoDemo } from "./examples/promo-demo/PromoDemo";
import { CourseDemo } from "./examples/course-demo/CourseDemo";
import promoEn from "../../examples/promo-demo/project.en.json";
import promoZh from "../../examples/promo-demo/project.zh.json";
import courseEn from "../../examples/course-demo/project.en.json";
import courseZh from "../../examples/course-demo/project.zh.json";

// Duration comes from the narration timing (or a text-length estimate in Studio).
const calculateMetadata: CalculateMetadataFunction<ExampleProps> = ({ props }) => {
  const { fps, width, height } = props.project.video;
  const { total } = buildShots(props.project.lines, props.timing, fps);
  return { durationInFrames: Math.max(1, total), fps, width, height };
};

const entries: { project: Project; component: React.FC<ExampleProps> }[] = [
  { project: promoEn as Project, component: PromoDemo },
  { project: promoZh as Project, component: PromoDemo },
  { project: courseEn as Project, component: CourseDemo },
  { project: courseZh as Project, component: CourseDemo },
];

export const Root: React.FC = () => (
  <>
    {entries.map(({ project, component }) => (
      <Composition
        key={project.id}
        id={project.video.composition}
        component={component}
        width={project.video.width}
        height={project.video.height}
        fps={project.video.fps}
        durationInFrames={300}
        defaultProps={{ project, timing: null, audioBase: null, opening3d: null } satisfies ExampleProps}
        calculateMetadata={calculateMetadata}
      />
    ))}
  </>
);
