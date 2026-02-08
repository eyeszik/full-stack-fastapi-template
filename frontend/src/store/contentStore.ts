import { create } from 'zustand'

interface ContentVariant {
  id: string
  content_id: string
  platform: string
  scheduled_for: string | null
  published_at: string | null
  platform_specific_data: Record<string, any>
  platform_post_id: string | null
  platform_url: string | null
}

interface Content {
  id: string
  title: string
  content_type: string
  status: string
  body: string | null
  campaign_id: string | null
  created_at: string
  variants: ContentVariant[]
}

interface ContentStore {
  contents: Content[]
  selectedContent: Content | null
  isLoading: boolean
  error: string | null

  // Actions
  setContents: (contents: Content[]) => void
  addContent: (content: Content) => void
  updateContent: (id: string, updates: Partial<Content>) => void
  deleteContent: (id: string) => void
  setSelectedContent: (content: Content | null) => void
  updateVariant: (contentId: string, variantId: string, updates: Partial<ContentVariant>) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useContentStore = create<ContentStore>((set) => ({
  contents: [],
  selectedContent: null,
  isLoading: false,
  error: null,

  setContents: (contents) => set({ contents }),

  addContent: (content) => set((state) => ({
    contents: [...state.contents, content]
  })),

  updateContent: (id, updates) => set((state) => ({
    contents: state.contents.map((c) =>
      c.id === id ? { ...c, ...updates } : c
    ),
    selectedContent: state.selectedContent?.id === id
      ? { ...state.selectedContent, ...updates }
      : state.selectedContent
  })),

  deleteContent: (id) => set((state) => ({
    contents: state.contents.filter((c) => c.id !== id),
    selectedContent: state.selectedContent?.id === id ? null : state.selectedContent
  })),

  setSelectedContent: (content) => set({ selectedContent: content }),

  updateVariant: (contentId, variantId, updates) => set((state) => ({
    contents: state.contents.map((content) =>
      content.id === contentId
        ? {
            ...content,
            variants: content.variants.map((v) =>
              v.id === variantId ? { ...v, ...updates } : v
            )
          }
        : content
    )
  })),

  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error })
}))
