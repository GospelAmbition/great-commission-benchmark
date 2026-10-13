import type { DetailedHTMLProps, HTMLAttributes } from "react";

// <helpinator-widget> is a custom element registered by the Helpinator script.
declare module "react" {
  namespace JSX {
    interface IntrinsicElements {
      "helpinator-widget": DetailedHTMLProps<HTMLAttributes<HTMLElement>, HTMLElement> & {
        host: string;
        "widget-id": string;
      };
    }
  }
}
