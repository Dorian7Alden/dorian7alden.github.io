import { execSync } from 'node:child_process';
import {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  writeFileSync,
} from 'node:fs';
import { basename, dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import matter from 'gray-matter';
import yaml from 'js-yaml';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');

const NOTES_REPO = 'D:/notes/Dorian-Alden-Dai-Personal-Notes';
const CONTENT_DIR = join(ROOT, 'content');

interface PostMeta {
  title: string;
  date: string;
  category: string;
  order: number;
  slug: string;
  file: string;
  hasFrontmatter: boolean;
}

interface CategoryInfo {
  name: string;
  count: number;
  posts: PostMeta[];
}

function isHidden(name: string): boolean {
  return name.startsWith('.');
}

function getGitDate(filePath: string): string {
  try {
    const date = execSync(
      `git log -1 --format=%aI -- "${filePath}"`,
      { cwd: NOTES_REPO, encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }
    ).trim();
    return date || new Date().toISOString().split('T')[0];
  } catch {
    return new Date().toISOString().split('T')[0];
  }
}

function parseFilename(filename: string): { order: number; rawTitle: string } {
  const match = filename.match(/^(\d+)-(.+)\.md$/);
  if (match) {
    return { order: parseInt(match[1], 10), rawTitle: match[2] };
  }
  const nameWithoutExt = filename.replace(/\.md$/, '');
  return { order: 0, rawTitle: nameWithoutExt };
}

function toDateString(val: string): string {
  // Normalize to YYYY-MM-DD
  return val.split('T')[0];
}

function processFile(filePath: string, category: string): PostMeta | null {
  const filename = basename(filePath);
  if (isHidden(filename) || !filename.endsWith('.md')) return null;

  const raw = readFileSync(filePath, 'utf-8');
  const parsed = matter(raw);
  const hasFrontmatter = Object.keys(parsed.data).length > 0;
  const { order, rawTitle } = parseFilename(filename);

  let title: string;
  let date: string;

  if (hasFrontmatter) {
    title = parsed.data.title || rawTitle;
    date = parsed.data.date || getGitDate(filePath);
  } else {
    title = rawTitle;
    date = getGitDate(filePath);
  }

  const slug = filename.replace(/\.md$/, '').replace(/[^\w一-鿿-]/g, '-')
    .replace(/-+/g, '-').replace(/^-|-$/g, '').toLowerCase() || 'untitled';

  const relPath = relative(NOTES_REPO, filePath);

  // Build new frontmatter, preserving any existing fields
  const newFrontmatter: Record<string, unknown> = { ...parsed.data };
  newFrontmatter.title = title;
  newFrontmatter.date = toDateString(String(newFrontmatter.date || date));
  newFrontmatter.category = category;
  newFrontmatter.order = newFrontmatter.order ?? order;

  // Escape HTML-comment-like patterns inside fenced code blocks.
  // Vue's SFC parser interprets --> as closing HTML comments,
  // which breaks when Java code has strings like "Logger-->前置通知".
  let safeContent = parsed.content;
  safeContent = safeContent.replace(
    /(`{3,}[\s\S]*?`{3,})/g,
    (fence: string) => fence.replace(/-->/g, '-​->')
  );

  // Serialize frontmatter + content with js-yaml
  const yamlStr = yaml.dump(newFrontmatter, { lineWidth: -1, noCompatMode: true });
  const outputContent = `---\n${yamlStr}---\n${safeContent}`;

  const outPath = join(CONTENT_DIR, relPath);
  mkdirSync(dirname(outPath), { recursive: true });
  writeFileSync(outPath, outputContent, 'utf-8');

  return {
    title,
    date: String(newFrontmatter.date),
    category,
    order: Number(newFrontmatter.order),
    slug,
    file: relPath,
    hasFrontmatter: !!hasFrontmatter,
  };
}

function walkDir(dir: string, category: string, posts: PostMeta[]): void {
  const entries = readdirSync(dir);

  for (const entry of entries) {
    if (isHidden(entry)) continue;
    const fullPath = join(dir, entry);
    const stat = statSync(fullPath);

    if (stat.isDirectory()) {
      walkDir(fullPath, entry, posts);
    } else if (stat.isFile() && entry.endsWith('.md')) {
      const post = processFile(fullPath, category);
      if (post) posts.push(post);
    }
  }
}

function generateCategories(posts: PostMeta[]): CategoryInfo[] {
  const map = new Map<string, PostMeta[]>();
  for (const post of posts) {
    const list = map.get(post.category) || [];
    list.push(post);
    map.set(post.category, list);
  }

  const categories: CategoryInfo[] = [];
  for (const [name, catPosts] of map) {
    catPosts.sort((a, b) => a.order - b.order);
    categories.push({ name, count: catPosts.length, posts: catPosts });
  }
  return categories;
}

function main(): void {
  console.log('Syncing notes to blog content...\n');

  if (existsSync(CONTENT_DIR)) {
    rmSync(CONTENT_DIR, { recursive: true, force: true });
  }
  mkdirSync(CONTENT_DIR, { recursive: true });

  const posts: PostMeta[] = [];

  const rootEntries = readdirSync(NOTES_REPO);

  for (const entry of rootEntries) {
    if (isHidden(entry)) continue;
    const fullPath = join(NOTES_REPO, entry);
    const stat = statSync(fullPath);

    if (stat.isDirectory()) {
      walkDir(fullPath, entry, posts);
    } else if (stat.isFile() && entry.endsWith('.md') && entry !== 'README.md') {
      const post = processFile(fullPath, '未分类');
      if (post) posts.push(post);
    }
  }

  // Sort by date (newest first), then by order
  posts.sort((a, b) => b.date.localeCompare(a.date) || a.order - b.order);

  const categories = generateCategories(posts);
  const summary = {
    total: posts.length,
    categories,
    posts: posts.map((p) => ({
      title: p.title,
      date: p.date,
      category: p.category,
      order: p.order,
      slug: p.slug,
      file: p.file,
      url: `/content/${p.file.replace(/\\/g, '/').replace(/\.md$/, '')}`,
    })),
  };

  writeFileSync(
    join(CONTENT_DIR, 'categories.json'),
    JSON.stringify(summary, null, 2),
    'utf-8'
  );

  console.log(`Total posts: ${posts.length}`);
  console.log('Categories:');
  for (const cat of categories) {
    console.log(`  ${cat.name}: ${cat.count} posts`);
  }
  console.log('\nSync complete.');
}

main();
