import type { Metadata } from 'next';
import './globals.css';
import Navbar from '@/components/Navbar';

export const metadata: Metadata = {
  title: {
    default: 'Google Photos AI Discovery Engine — Insights Dashboard',
    template: '%s — AI Discovery Engine',
  },
  description: 'Analyzing visual memory retrieval friction in Google Photos — understanding how users recall past visual memories, where retrieval breaks down when memory is incomplete, and identifying opportunities for AI-native episodic retrieval.',
  keywords: ['Google Photos', 'analytics', 'consumer insights', 'discovery engine', 'AI research'],
  authors: [{ name: 'AI Discovery Engine' }],
  openGraph: {
    title: 'Google Photos AI Discovery Engine — Insights Dashboard',
    description: 'Analyzing visual memory retrieval friction in Google Photos — understanding how users recall past visual memories, where retrieval breaks down when memory is incomplete, and identifying opportunities for AI-native episodic retrieval.',
    type: 'website',
    siteName: 'AI Discovery Engine',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-mode="dark" data-theme="midnight-observatory" data-scroll-behavior="smooth" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var m = localStorage.getItem('app-mode') || 'dark';
                  var t = localStorage.getItem('app-theme') || 'midnight-observatory';
                  // Remap legacy themes
                  var remap = {
                    'google-lens':'midnight-observatory','tokyo-sakura':'midnight-observatory','sunset':'midnight-observatory',
                    'darkroom':'sunrise-warm','cosmic-nebula':'sunrise-warm',
                    'nordic-gallery':'deep-ocean','cyber-matrix':'deep-ocean','cyber':'deep-ocean','emerald':'deep-ocean',
                    'warm-studio':'volcanic-ember','solar-flare':'volcanic-ember'
                  };
                  if (remap[t]) { t = remap[t]; localStorage.setItem('app-theme', t); }
                  document.documentElement.setAttribute('data-mode', m);
                  document.documentElement.setAttribute('data-theme', t);

                  // Strip third-party extension attributes
                  if (typeof MutationObserver !== 'undefined') {
                    var observer = new MutationObserver(function(mutations) {
                      for (var i = 0; i < mutations.length; i++) {
                        var mut = mutations[i];
                        if (mut.type === 'attributes' && mut.attributeName === 'bis_skin_checked') {
                          mut.target.removeAttribute('bis_skin_checked');
                        }
                      }
                    });
                    observer.observe(document.documentElement, {
                      attributes: true, subtree: true, attributeFilter: ['bis_skin_checked']
                    });
                  }
                } catch (e) {}
              })();
            `,
          }}
        />
      </head>
      <body suppressHydrationWarning>
        <a href="#main-content" className="skip-link" suppressHydrationWarning>
          Skip to main content
        </a>
        <Navbar />
        <main id="main-content" tabIndex={-1} className="page-wrapper" suppressHydrationWarning>
          {children}
        </main>
      </body>
    </html>
  );
}
