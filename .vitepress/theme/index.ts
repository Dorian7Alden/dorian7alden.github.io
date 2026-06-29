import type { Theme } from 'vitepress'
import PostList from './components/blog/PostList.vue'
import PostCard from './components/blog/PostCard.vue'
import CategoryNav from './components/blog/CategoryNav.vue'
import CategoriesPage from './components/page/CategoriesPage.vue'
import PersonalCard from './components/blog/PersonalCard.vue'
import ContributionHeatmap from './components/blog/ContributionHeatmap.vue'
import FloatingSidebar from './components/blog/FloatingSidebar.vue'
import NoteTreePanel from './components/blog/NoteTreePanel.vue'
import AboutPage from './components/page/AboutPage.vue'
import CustomLayout from './CustomLayout.vue'
import './styles/main.css'

export default {
  extends: undefined,
  Layout: CustomLayout,
  enhanceApp({ app }) {
    app.component('PostList', PostList)
    app.component('PostCard', PostCard)
    app.component('CategoryNav', CategoryNav)
    app.component('CategoriesPage', CategoriesPage)
    app.component('PersonalCard', PersonalCard)
    app.component('ContributionHeatmap', ContributionHeatmap)
    app.component('FloatingSidebar', FloatingSidebar)
    app.component('NoteTreePanel', NoteTreePanel)
    app.component('AboutPage', AboutPage)
  },
} satisfies Theme
