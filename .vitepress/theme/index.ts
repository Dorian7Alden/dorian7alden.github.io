import type { Theme } from 'vitepress'
import PostList from './components/PostList.vue'
import PostCard from './components/PostCard.vue'
import CategoryNav from './components/CategoryNav.vue'
import CategoriesPage from './components/CategoriesPage.vue'
import HeroSection from './components/HeroSection.vue'
import NoteTreePanel from './components/NoteTreePanel.vue'
import AboutPage from './components/AboutPage.vue'
import CustomLayout from './CustomLayout.vue'
import './style.css'

export default {
  extends: undefined,
  Layout: CustomLayout,
  enhanceApp({ app }) {
    app.component('PostList', PostList)
    app.component('PostCard', PostCard)
    app.component('CategoryNav', CategoryNav)
    app.component('CategoriesPage', CategoriesPage)
    app.component('HeroSection', HeroSection)
    app.component('NoteTreePanel', NoteTreePanel)
    app.component('AboutPage', AboutPage)
  },
} satisfies Theme
