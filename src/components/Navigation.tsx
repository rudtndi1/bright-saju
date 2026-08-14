'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { href: '/', label: '사주', icon: '����' },
  { href: '/taro', label: '타로', icon: '����' },
  { href: '/daily', label: '오늘운세', icon: '�����' },
  { href: '/compatibility', label: '궁합', icon: '����' },
] as const;

export function Navigation() {
  const [scrolled, setScrolled] = useState(false);
  const [mounted, setMounted] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    setMounted(true);
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  if (!mounted) {
    return (
      <nav style={{ height: 'var(--nav-height)' }} aria-hidden="true">
        <div className="container" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span className="brand" style={{ fontSize: 'var(--fs-xl)', fontWeight: 700, letterSpacing: '0.02em' }}>
            사주, <span style={{ color: 'var(--color-jujube)' }}>다시 읽다</span>
          </span>
        </div>
      </nav>
    );
  }

  return (
    <nav
      className="serif"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 50,
        height: 'var(--nav-height)',
        backdropFilter: 'blur(10px)',
        background: scrolled ? 'rgba(243, 237, 226, 0.92)' : 'rgba(243, 237, 226, 0.78)',
        borderBottom: `1px solid ${scrolled ? 'var(--color-line-strong)' : 'var(--color-line)'}`,
        transition: 'background var(--transition-base), border-color var(--transition-base)',
      }}
      role="navigation"
      aria-label="메인 내비게이션"
    >
      <div className="container" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Link
          href="/"
          className="brand"
          style={{
            fontSize: 'var(--fs-xl)',
            fontWeight: 700,
            letterSpacing: '0.02em',
            color: 'var(--color-ink)',
          }}
          aria-label="사주, 다시 읽다 - 홈으로"
        >
          사주, <span style={{ color: 'var(--color-jujube)' }}>다시 읽다</span>
        </Link>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
          <div style={{ display: 'flex', gap: 'var(--space-1)', background: 'var(--color-bg-card)', border: '1px solid var(--color-line)', borderRadius: 'var(--radius-full)', padding: 'var(--space-1)' }}>
            {navItems.map(item => (
              <Link
                key={item.href}
                href={item.href}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 'var(--space-2)',
                  padding: 'var(--space-2) var(--space-4)',
                  borderRadius: 'var(--radius-full)',
                  fontSize: 'var(--fs-sm)',
                  fontWeight: pathname === item.href ? 600 : 500,
                  color: pathname === item.href ? 'var(--color-jujube)' : 'var(--color-ink-soft)',
                  background: pathname === item.href ? 'var(--color-jujube-pale)' : 'transparent',
                  transition: 'all var(--transition-fast)',
                  whiteSpace: 'nowrap',
                }}
                aria-current={pathname === item.href ? 'page' : undefined}
              >
                <span aria-hidden="true">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            ))}
          </div>

          <a
            href="https://pf.kakao.com/" // TODO: 실제 카카오 채널 ��크
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-gold"
            style={{ fontSize: 'var(--fs-sm)', padding: 'var(--space-2) var(--space-5)' }}
            aria-label="카카오��� 채널 상담하기"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.27-.099-.47-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.466-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.488.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347-.298-.149-1.044-.538-1.518-.793-.456-.247-.914-.394-1.35-.524-.436-.133-.899-.193-1.34-.148-.458.046-.89.273-1.252.523-.361.25-.623.413-.79.471z"/>
              <path d="M12 2C6.486 2 2 6.486 2 12c0 4.411 3.002 8.178 7.111 9.479.56.145.766-.388.766-.866 0-.431-.017-1.572-.023-3.088-2.887.625-3.495-1.387-3.495-1.387-.471-1.197-1.15-1.513-1.15-1.513-.938-.642.072-.628.072-.628 1.037.074 1.58 1.076 1.58 1.076.922 1.574 2.416 1.12 3.002.858.094-.666.36-1.12.656-1.378-2.29-.26-4.7-.116-4.7-4.75 0-1.048.38-1.903 1.003-2.573-.1-.242-.436-1.222.096-2.54 0 0 .82-.256 2.68 1.002A9.578 9.578 0 0112 6.84c.85.004 1.705.114 2.504.337 1.86-1.258 2.68-1.002 2.68-1.002.532 1.318.197 2.298.1 2.54.62.67 1.003 1.525 1.003 2.573 0 4.604-2.409 4.75-4.77 4.75.376.297.71.884.71 1.785 0 1.287-.013 2.322-.013 2.636 0 .48.205 1.014.77.86C20.998 20.178 24 16.411 24 12c0-5.514-4.486-10-10-10z"/>
            </svg>
            상담하기
          </a>
        </div>
      </div>
    </nav>
  );
}