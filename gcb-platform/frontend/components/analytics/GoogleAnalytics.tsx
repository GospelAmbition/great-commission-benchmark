import Script from "next/script";

/** Google Analytics (gtag.js). Remove this component and its use in app/layout.tsx when switching to a permanent analytics solution. */
const GA_MEASUREMENT_ID = "G-3E6906Q9KE";

export function GoogleAnalytics() {
  return (
    <>
      <Script
        id="gtag-init"
        strategy="beforeInteractive"
        dangerouslySetInnerHTML={{
          __html: `
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', '${GA_MEASUREMENT_ID}');
          `,
        }}
      />
      <Script
        src={`https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`}
        strategy="afterInteractive"
      />
    </>
  );
}
