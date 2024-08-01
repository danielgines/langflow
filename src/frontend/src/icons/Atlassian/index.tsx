import React, { forwardRef } from "react";
import SvgAtlassian from "./Atlassian";

export const AtlassianIcon = forwardRef<
  SVGSVGElement,
  React.PropsWithChildren<{}>
>((props, ref) => {
  return <SvgAtlassian ref={ref} {...props} />;
});