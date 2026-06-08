import { execSync } from 'node:child_process';
import {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  writeFileSync,
  copyFileSync,
} from 'node:fs';
import { basename, dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import matter from 'gray-matter';
import yaml from 'js-yaml';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');

const notesRepoFromEnv = process.env.NOTES_REPO;
const siblingNotesRepo = join(ROOT, '..', 'notes-source');
const NOTES_REPO = notesRepoFromEnv || (existsSync(siblingNotesRepo) ? siblingNotesRepo : 'D:/notes/kualk-learn-notes');
const CONTENT_DIR = process.env.CONTENT_DIR
  ? join(ROOT, process.env.CONTENT_DIR)
  : join(ROOT, 'generated', 'notes');

interface PostMeta {
  title: string;
  date: string;
  category: string;
  order: number;
  slug: string;
  file: string;
  pathSegments: string[];
  hasFrontmatter: boolean;
}

interface PostSummary extends PostMeta {
  url: string;
}

interface CategoryInfo {
  name: string;
  count: number;
  posts: PostSummary[];
}

interface NoteTreeNode {
  name: string;
  type: 'directory' | 'file';
  path: string;
  count: number;
  title?: string;
  url?: string;
  date?: string;
  order?: number;
  children?: NoteTreeNode[];
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
  return val.split('T')[0];
}

function toPosixPath(path: string): string {
  return path.replace(/\\/g, '/');
}

function copyAssets(dir: string, outDir: string): void {
  for (const entry of readdirSync(dir)) {
    if (isHidden(entry) || entry.endsWith('.md')) continue;

    const source = join(dir, entry);
    const target = join(outDir, entry);
    const stat = statSync(source);

    if (stat.isDirectory()) {
      copyAssets(source, target);
    } else if (stat.isFile()) {
      mkdirSync(dirname(target), { recursive: true });
      copyFileSync(source, target);
    }
  }
}

function escapeVueHtml(raw: string): string {
  return raw.replace(/<(?!\/?(?:script|style|template)(?=\s|>|$))/gi, '&lt;');
}

function sanitizeMarkdownImages(filePath: string, raw: string): string {
  return raw.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt: string, src: string) => {
    const trimmedSrc = src.trim();

    if (/^(https?:|data:|\/)/i.test(trimmedSrc)) {
      return match;
    }

    if (/^[A-Za-z]:\\/.test(trimmedSrc)) {
      return `*[图片缺失：${alt}]*`;
    }

    const normalizedSrc = trimmedSrc.replace(/\\/g, '/');
    const sourceDir = dirname(filePath);
    const directTarget = join(sourceDir, normalizedSrc);

    if (existsSync(directTarget)) {
      return `![${alt}](${normalizedSrc})`;
    }

    let currentDir = sourceDir;
    while (currentDir.startsWith(NOTES_REPO)) {
      const candidate = join(currentDir, normalizedSrc);
      if (existsSync(candidate)) {
        const fixedSrc = toPosixPath(relative(sourceDir, candidate));
        return `![${alt}](${fixedSrc})`;
      }

      const parentDir = dirname(currentDir);
      if (parentDir === currentDir) break;
      currentDir = parentDir;
    }

    return `*[图片缺失：${alt}]*`;
  });
}

function getPostUrl(file: string): string {
  return `/generated/notes/${toPosixPath(file).replace(/\.md$/, '')}`;
}

function processFile(filePath: string, pathSegments: string[]): PostMeta | null {
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
  const category = pathSegments[0] || '未分类';

  // Build new frontmatter, preserving any existing fields
  const newFrontmatter: Record<string, unknown> = { ...parsed.data };
  newFrontmatter.title = title;
  newFrontmatter.date = toDateString(String(newFrontmatter.date || date));
  newFrontmatter.category = category;
  newFrontmatter.path = pathSegments.join('/');
  newFrontmatter.order = newFrontmatter.order ?? order;

  // Escape HTML-comment-like patterns inside fenced code blocks.
  // Vue's SFC parser interprets --> as closing HTML comments,
  // which breaks when Java code has strings like "Logger-->前置通知".
  let safeContent = sanitizeMarkdownImages(filePath, escapeVueHtml(parsed.content));
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
    pathSegments,
    hasFrontmatter: !!hasFrontmatter,
  };
}

function walkDir(dir: string, pathSegments: string[], posts: PostMeta[]): void {
  const entries = readdirSync(dir);

  for (const entry of entries) {
    if (isHidden(entry)) continue;
    const fullPath = join(dir, entry);
    const stat = statSync(fullPath);

    if (stat.isDirectory()) {
      walkDir(fullPath, [...pathSegments, entry], posts);
    } else if (stat.isFile() && entry.endsWith('.md')) {
      const post = processFile(fullPath, pathSegments);
      if (post) posts.push(post);
    }
  }
}

function toPostSummary(post: PostMeta): PostSummary {
  return {
    ...post,
    file: toPosixPath(post.file),
    url: getPostUrl(post.file),
  };
}

function generateCategories(posts: PostSummary[]): CategoryInfo[] {
  const map = new Map<string, PostSummary[]>();
  for (const post of posts) {
    const list = map.get(post.category) || [];
    list.push(post);
    map.set(post.category, list);
  }

  const categories: CategoryInfo[] = [];
  for (const [name, catPosts] of map) {
    catPosts.sort((a, b) => a.order - b.order || a.title.localeCompare(b.title, 'zh-CN'));
    categories.push({ name, count: catPosts.length, posts: catPosts });
  }
  return categories.sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'));
}

function sortTree(nodes: NoteTreeNode[]): NoteTreeNode[] {
  return nodes.sort((a, b) => {
    if (a.type !== b.type) return a.type === 'directory' ? -1 : 1;
    return (a.order ?? 0) - (b.order ?? 0) || a.name.localeCompare(b.name, 'zh-CN');
  }).map((node) => ({
    ...node,
    children: node.children ? sortTree(node.children) : undefined,
  }));
}

function generateNoteTree(posts: PostSummary[]): NoteTreeNode[] {
  const root: NoteTreeNode[] = [];

  for (const post of posts) {
    let level = root;
    let currentPath = '';

    for (const segment of post.pathSegments) {
      currentPath = currentPath ? `${currentPath}/${segment}` : segment;
      let dirNode = level.find((node) => node.type === 'directory' && node.name === segment);
      if (!dirNode) {
        dirNode = {
          name: segment,
          type: 'directory',
          path: currentPath,
          count: 0,
          children: [],
        };
        level.push(dirNode);
      }
      dirNode.count += 1;
      level = dirNode.children || [];
    }

    level.push({
      name: basename(post.file).replace(/\.md$/, ''),
      title: post.title,
      type: 'file',
      path: toPosixPath(post.file),
      count: 1,
      url: post.url,
      date: post.date,
      order: post.order,
    });
  }

  return sortTree(root);
}

function main(): void {
  console.log('Syncing notes to blog content...\n');

  if (existsSync(CONTENT_DIR)) {
    rmSync(CONTENT_DIR, { recursive: true, force: true });
  }
  mkdirSync(CONTENT_DIR, { recursive: true });
  copyAssets(NOTES_REPO, CONTENT_DIR);

  const posts: PostMeta[] = [];

  const rootEntries = readdirSync(NOTES_REPO);

  for (const entry of rootEntries) {
    if (isHidden(entry)) continue;
    const fullPath = join(NOTES_REPO, entry);
    const stat = statSync(fullPath);

    if (stat.isDirectory()) {
      walkDir(fullPath, [entry], posts);
    } else if (stat.isFile() && entry.endsWith('.md') && entry !== 'README.md') {
      const post = processFile(fullPath, []);
      if (post) posts.push(post);
    }
  }

  // Sort by date (newest first), then by order
  posts.sort((a, b) => b.date.localeCompare(a.date) || a.order - b.order);

  const postSummaries = posts.map(toPostSummary);
  const categories = generateCategories(postSummaries);
  const tree = generateNoteTree(postSummaries);
  const summary = {
    total: postSummaries.length,
    categories,
    tree,
    posts: postSummaries,
  };

  writeFileSync(
    join(CONTENT_DIR, 'categories.json'),
    JSON.stringify(summary, null, 2),
    'utf-8'
  );

  console.log(`Total posts: ${postSummaries.length}`);
  console.log('Directories:');
  for (const node of tree) {
    console.log(`  ${node.name}: ${node.count} posts`);
  }
  console.log('\nSync complete.');
}

main();
