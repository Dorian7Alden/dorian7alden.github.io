---
layout: page
---

<script setup>
import { withBase } from 'vitepress'
</script>

<div class="about-page">

<div class="about-hero">
  <div class="about-avatar">
    <img :src="withBase('/avatar.jpg')" alt="Dorian7Alden 头像" />
  </div>
  <h1 class="about-name">Dorian Alden Dai</h1>
  <p class="about-bio">软件工程专业大学生，热爱技术，持续学习中</p>
</div>

<div class="about-section">
  <h2>关于本站</h2>
  <p>这个博客记录我的技术学习笔记、遇到的问题和排查过程。内容源自我在学习和实践中记录的笔记，通过 VitePress 构建成静态网站分享出来。</p>
  <p>如果我的笔记能帮到你，那就太好了。</p>
</div>

<div class="about-section">
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
  </div>
</div>

<div class="about-section">
  <h2>联系方式</h2>
  <div class="contact-links">
    <a href="https://github.com/Dorian7Alden" target="_blank" rel="noopener" class="contact-link">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
      GitHub
    </a>
  </div>
</div>

</div>

<style>
.about-page {
  max-width: 640px;
  margin: 0 auto;
  padding: 0 24px 48px;
}

.about-hero {
  text-align: center;
  padding: 48px 0 40px;
}

.about-avatar {
  width: 96px;
  height: 96px;
  margin: 0 auto 20px;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  border: 3px solid #fff;
  background: var(--bg-card);
}

.about-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.about-name {
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.5px;
  color: var(--text-heading);
  margin: 0 0 8px;
}

.about-bio {
  font-size: 1.05rem;
  color: var(--vp-c-text-2);
  margin: 0;
}

.about-section {
  margin: 36px 0;
}

.about-section h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-heading);
  margin: 0 0 16px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--vp-c-divider);
}

.about-section p {
  color: var(--vp-c-text-2);
  line-height: 1.8;
  margin: 0.6rem 0;
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  display: inline-block;
  padding: 6px 14px;
  background: var(--brand-soft);
  color: var(--brand-dark);
  font-size: 0.88rem;
  font-weight: 550;
  border-radius: var(--radius-full);
  transition: all var(--duration-fast);
}

.tag:hover {
  background: var(--brand);
  color: #fff;
}

.contact-links {
  display: flex;
  gap: 12px;
}

.contact-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 18px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  text-decoration: none;
  border-radius: var(--radius-full);
  font-size: 0.9rem;
  font-weight: 550;
  border: 1px solid var(--vp-c-border);
  transition: all var(--duration-normal) var(--ease-out);
}

.contact-link:hover {
  border-color: var(--brand);
  color: var(--brand);
  background: var(--brand-soft);
}
</style>
