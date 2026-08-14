import type { Metadata, Viewport } from 'next';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: '사주, 다시 읽다',
  description: '사주·타로·오늘운세·궁합 — 내 운명을 오늘의 언어로 풀어드립니다.',
  keywords: ['사주', '타로', '운세', '궁합', '만세력', '대운', '십성'],
  authors: [{ name: '사주, 다시 읽다' }],
  openGraph: {
    title: '사주, 다시 읽다',
    description: '사주·타로·오늘운세·궁합 — 내 운명을 오늘의 언어로 풀어드립니다.',
    type: 'website',
    locale: 'ko_KR',
    siteName: '사주, 다시 읽다',
  },
  twitter: {
    card: 'summary_large_image',
    title: '사주, 다시 읽다',
    description: '사주·타로·오늘운세·궁합 — 내 운명을 오늘의 언어로 풀어드립니다.',
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  themeColor: '#f3ede2',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;500;700;900&family=Pretendard:wght@300;400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}