<script setup lang="ts">
import { withBase } from 'vitepress'
</script>

<template>
  <div class="about-page">
    <section class="profile-card">
      <div class="profile-bg"></div>
      <div class="about-avatar">
        <img :src="withBase('/avatar.jpg')" alt="Dorian7Alden 头像" />
      </div>
      <span class="profile-kicker">About Me</span>
      <h1 class="about-name">Dorian Alden Dai</h1>
      <p class="about-bio">软件工程专业学生，关注后端工程、AI 工具与持续学习实践。</p>
      <div class="profile-actions">
        <a href="https://github.com/Dorian7Alden" target="_blank" rel="noopener" class="contact-link primary">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
          GitHub · Dorian7Alden
        </a>
      </div>
    </section>

    <section class="about-grid">
      <article class="about-section intro-card">
        <span class="section-kicker">Blog</span>
        <h2>关于本站</h2>
        <p>这个博客记录我的技术学习笔记、遇到的问题和排查过程。内容源自我在学习和实践中沉淀的原始笔记，通过 VitePress 自动构建成静态网站。</p>
        <p>我希望这里不只是文章列表，而是一套持续更新的个人知识库：保留真实问题、复盘路径和可复用经验。</p>
      </article>

      <article class="about-section">
        <span class="section-kicker">Focus</span>
        <h2>技术方向</h2>
        <div class="skill-tags">
          <span class="tag">Java</span>
          <span class="tag">Spring Boot</span>
          <span class="tag">Spring Cloud</span>
          <span class="tag">MySQL</span>
          <span class="tag">Redis</span>
          <span class="tag">Git</span>
          <span class="tag">Docker</span>
          <span class="tag">CI/CD</span>
          <span class="tag">Vue 3</span>
          <span class="tag">VitePress</span>
          <span class="tag">AI Tools</span>
        </div>
      </article>
    </section>
  </div>
</template>

<style scoped>
.about-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 12px 24px 68px;
}

.profile-card {
  position: relative;
  overflow: hidden;
  text-align: center;
  padding: 52px 28px 40px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 34px;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--bg-card) 96%, transparent), color-mix(in srgb, var(--bg-card) 80%, transparent)),
    radial-gradient(circle at 18% 0%, var(--brand-soft), transparent 42%),
    radial-gradient(circle at 82% 8%, var(--accent-soft), transparent 36%);
  box-shadow: var(--shadow-lg);
}

.profile-bg {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(rgba(79, 109, 245, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(79, 109, 245, 0.06) 1px, transparent 1px);
  background-size: 46px 46px;
  mask-image: radial-gradient(circle at 50% 20%, #000 0%, transparent 68%);
  pointer-events: none;
}

.about-avatar {
  position: relative;
  width: 122px;
  height: 122px;
  margin: 0 auto 20px;
  padding: 5px;
  border-radius: 32px;
  overflow: hidden;
  background: linear-gradient(135deg, var(--brand-light), var(--accent));
  box-shadow: 0 18px 42px color-mix(in srgb, var(--brand) 24%, transparent);
}

.about-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  border-radius: 27px;
  border: 4px solid var(--bg-card);
}

.profile-kicker,
.section-kicker {
  display: inline-flex;
  color: var(--brand);
  font-size: 0.78rem;
  font-weight: 900;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.about-name {
  position: relative;
  font-size: clamp(2.1rem, 5vw, 3.4rem);
  line-height: 1.06;
  font-weight: 900;
  letter-spacing: -0.07em;
  color: var(--text-heading);
  margin: 10px 0;
}

.about-bio {
  position: relative;
  max-width: 560px;
  margin: 0 auto;
  font-size: 1.06rem;
  line-height: 1.8;
  color: var(--vp-c-text-2);
}

.profile-actions {
  position: relative;
  display: flex;
  justify-content: center;
  margin-top: 26px;
}

.about-grid {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 18px;
  margin-top: 22px;
}

.about-section {
  padding: 28px;
  border-radius: var(--radius-xl);
  border: 1px solid var(--vp-c-divider);
  background: var(--bg-card);
  box-shadow: var(--shadow-sm);
}

.about-section h2 {
  font-size: 1.36rem;
  line-height: 1.2;
  font-weight: 900;
  letter-spacing: -0.04em;
  color: var(--text-heading);
  margin: 8px 0 16px;
}

.about-section p {
  color: var(--vp-c-text-2);
  line-height: 1.85;
  margin: 0.7rem 0;
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
}

.tag {
  display: inline-flex;
  padding: 7px 13px;
  background: var(--brand-soft);
  color: var(--brand);
  font-size: 0.86rem;
  font-weight: 800;
  border-radius: var(--radius-full);
  border: 1px solid color-mix(in srgb, var(--brand) 15%, transparent);
  transition: all var(--duration-fast);
}

.tag:hover {
  background: var(--brand);
  color: #fff;
  transform: translateY(-1px);
}

.contact-link {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 11px 18px;
  color: var(--vp-c-text-1);
  text-decoration: none;
  border-radius: var(--radius-full);
  font-size: 0.94rem;
  font-weight: 800;
  border: 1px solid var(--vp-c-border);
  transition: all var(--duration-normal) var(--ease-out);
}

.contact-link.primary {
  background: linear-gradient(135deg, var(--brand), var(--brand-light));
  color: #fff;
  border-color: transparent;
  box-shadow: 0 14px 28px color-mix(in srgb, var(--brand) 25%, transparent);
}

.contact-link:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

@media (max-width: 760px) {
  .about-page {
    padding: 0 16px 44px;
  }

  .profile-card {
    padding: 40px 22px 32px;
  }

  .about-grid {
    grid-template-columns: 1fr;
  }
}
</style>
