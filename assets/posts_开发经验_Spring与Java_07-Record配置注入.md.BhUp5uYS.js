import{_ as s,a,c as p,b as e}from"./chunks/framework.b9WMfGr4.js";const u=JSON.parse('{"title":"07-Record配置注入","description":"","frontmatter":{"title":"07-Record配置注入"},"headers":[],"relativePath":"posts/开发经验/Spring与Java/07-Record配置注入.md","filePath":"posts/开发经验/Spring与Java/07-Record配置注入.md"}'),l={name:"posts/开发经验/Spring与Java/07-Record配置注入.md"};function i(r,n,t,c,o,d){return a(),p("div",null,[...n[0]||(n[0]=[e(`<div class="language- vp-adaptive-theme line-numbers-mode"><button title="Copy Code" class="copy"></button><button class="collapse-btn" title="折叠代码" aria-label="折叠代码"><svg class="collapse-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg></button><span class="lang"></span><pre class="shiki shiki-themes github-light one-dark-pro vp-code" tabindex="0"><code><span class="line"><span>@ConfigurationProperties(prefix = &quot;swu&quot;)</span></span>
<span class="line"><span>public record SwuProperties(</span></span>
<span class="line"><span>        String key,</span></span>
<span class="line"><span>        String UA,</span></span>
<span class="line"><span>        String defaultAvatarUrl,</span></span>
<span class="line"><span>        Waf waf,</span></span>
<span class="line"><span>        Email email,</span></span>
<span class="line"><span>        Miniapp miniapp,</span></span>
<span class="line"><span>        Jw jw</span></span>
<span class="line"><span>) {</span></span>
<span class="line"><span>    public record Waf(String ip) {}</span></span>
<span class="line"><span>    public record Email(String alias) {}</span></span>
<span class="line"><span>    public record Miniapp(String appid, String appsecret) {}</span></span>
<span class="line"><span>    public record Jw(String xnm, String xqm, String xnmmc, String xqmmc) {}</span></span>
<span class="line"><span>}</span></span></code></pre><div class="line-numbers-wrapper" aria-hidden="true"><span class="line-number">1</span><br><span class="line-number">2</span><br><span class="line-number">3</span><br><span class="line-number">4</span><br><span class="line-number">5</span><br><span class="line-number">6</span><br><span class="line-number">7</span><br><span class="line-number">8</span><br><span class="line-number">9</span><br><span class="line-number">10</span><br><span class="line-number">11</span><br><span class="line-number">12</span><br><span class="line-number">13</span><br><span class="line-number">14</span><br><span class="line-number">15</span><br></div><div class="code-collapsed-indicator"><span class="code-collapsed-text">已折叠代码，点击展开</span><svg class="expand-icon" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg></div></div>`,1)])])}const m=s(l,[["render",i]]);export{u as __pageData,m as default};
