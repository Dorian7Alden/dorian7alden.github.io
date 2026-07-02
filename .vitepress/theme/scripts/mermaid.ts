import mermaid from 'mermaid'
import { useRouter } from 'vitepress'
import { onMounted, watch, nextTick } from 'vue'

mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
})

export function useMermaid() {
  const run = async () => {
    await nextTick()
    try {
      await mermaid.run({ querySelector: '.mermaid' })
    } catch {
      // mermaid 解析失败时静默忽略，避免阻塞页面
    }
  }

  if (typeof window !== 'undefined') {
    onMounted(run)

    const router = useRouter()
    watch(
      () => router.route.path,
      () => run(),
    )
  }
}
