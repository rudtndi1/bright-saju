import Link from 'next/link';

export function Footer() {
  return (
    <footer
      style={{
        background: 'var(--color-bg-deep)',
        borderTop: '1px solid var(--color-line)',
        padding: 'var(--space-16) 0 var(--space-8)',
        marginTop: 'var(--space-24)',
        position: 'relative',
        zIndex: 2,
      }}
      role="contentinfo"
    >
      <div className="container">
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            gap: 'var(--space-8)',
            marginBottom: 'var(--space-12)',
          }}
        >
          <div>
            <div className="brand serif" style={{ fontSize: 'var(--fs-2xl)', fontWeight: 700, marginBottom: 'var(--space-4)' }}>
              사주, <span style={{ color: 'var(--color-jujube)' }}>다시 읽다</span>
            </div>
            <p style={{ color: 'var(--color-ink-soft)', fontSize: 'var(--fs-md)', lineHeight: 'var(--lh-relaxed)', maxWidth: '320px' }}>
              태어난 네 글자를, 오늘의 언어로.<br />
              사주·타로·운세·궁합으로 내 운명을 읽어보세요.
            </p>
          </div>

          <nav aria-label="서비스 메뉴">
            <h3 style={{ fontSize: 'var(--fs-sm)', fontWeight: 700, color: 'var(--color-ink)', marginBottom: 'var(--space-3)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              서비스
            </h3>
            <ul style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              <li><Link href="/" style={{ color: 'var(--color-ink-soft)', fontSize: 'var(--fs-md)', transition: 'color var(--transition-fast)' }}>사주 ��이</Link></li>
              <li><Link href="/taro" style={{ color: 'var(--color-ink-soft)', fontSize: 'var(--fs-md)', transition: 'color var(--transition-fast)' }}>타로 리딩</Link></li>
              <li><Link href="/daily" style={{ color: 'var(--color-ink-soft)', fontSize: 'var(--fs-md)', transition: 'color var(--transition-fast)' }}>오늘 운세</Link></li>
              <li><Link href="/compatibility" style={{ color: 'var(--color-ink-soft)', fontSize: 'var(--fs-md)', transition: 'color var(--transition-fast)' }}>궁합 보기</Link></li>
            </ul>
          </nav>

          <nav aria-label="채널">
            <h3 style={{ fontSize: 'var(--fs-sm)', fontWeight: 700, color: 'var(--color-ink)', marginBottom: 'var(--space-3)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              채널
            </h3>
            <ul style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              <li><a href="https://www.youtube.com/" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--color-ink-soft)', fontSize: 'var(--fs-md)', transition: 'color var(--transition-fast)' }}>유튜브</a></li>
              <li><a href="https://pf.kakao.com/" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--color-ink-soft)', fontSize: 'var(--fs-md)', transition: 'color var(--transition-fast)' }}>카카오��� 채널</a></li>
            </ul>
          </nav>

          <div>
            <h3 style={{ fontSize: 'var(--fs-sm)', fontWeight: 700, color: 'var(--color-ink)', marginBottom: 'var(--space-3)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              연락처
            </h3>
            <address style={{ fontStyle: 'normal', color: 'var(--color-ink-soft)', fontSize: 'var(--fs-md)', lineHeight: 'var(--lh-relaxed)' }}>
              상담 문의: 카카오��� 채널<br />
              운영 시간: 평일 10:00 ~ 20:00
            </address>
          </div>
        </div>

        <div
          style={{
            borderTop: '1px solid var(--color-line)',
            paddingTop: 'var(--space-8)',
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 'var(--space-4)',
            fontSize: 'var(--fs-sm)',
            color: 'var(--color-ink-muted)',
          }}
        >
          <p>
            이 서비스는 엔터테인먼트 목적입니다. 중요한 결정은 전문가와 상담하세요.
          </p>
          <p>
            사주 계산: <a href="https://github.com/yhj1024/manseryeok" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--color-jujube)', textDecoration: 'underline' }}>manseryeok</a> (MIT License) © Yoohyojun
          </p>
        </div>
      </div>
    </footer>
  );
}