import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import Placeholder from '@tiptap/extension-placeholder'
import { Box, Button, HStack, useColorMode, IconButton, Separator } from '@chakra-ui/react'
import {
  FaBold,
  FaItalic,
  FaStrikethrough,
  FaCode,
  FaListUl,
  FaListOl,
  FaQuoteLeft,
  FaUndo,
  FaRedo,
  FaLink,
  FaImage,
  FaHeading
} from 'react-icons/fa'

interface ContentEditorProps {
  content: string
  onChange: (content: string) => void
  placeholder?: string
  minHeight?: string
}

export const ContentEditor: React.FC<ContentEditorProps> = ({
  content,
  onChange,
  placeholder = 'Start writing your content...',
  minHeight = '300px'
}) => {
  const { colorMode } = useColorMode()

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3]
        }
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'tiptap-link'
        }
      }),
      Image.configure({
        HTMLAttributes: {
          class: 'tiptap-image'
        }
      }),
      Placeholder.configure({
        placeholder
      })
    ],
    content,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML())
    },
    editorProps: {
      attributes: {
        class: 'tiptap-editor'
      }
    }
  })

  if (!editor) {
    return null
  }

  const addLink = () => {
    const url = window.prompt('Enter URL:')
    if (url) {
      editor.chain().focus().setLink({ href: url }).run()
    }
  }

  const addImage = () => {
    const url = window.prompt('Enter image URL:')
    if (url) {
      editor.chain().focus().setImage({ src: url }).run()
    }
  }

  return (
    <Box
      borderWidth="1px"
      borderRadius="md"
      borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.300'}
      overflow="hidden"
    >
      {/* Toolbar */}
      <Box
        padding={2}
        backgroundColor={colorMode === 'dark' ? 'gray.700' : 'gray.100'}
        borderBottomWidth="1px"
        borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.300'}
      >
        <HStack gap={1} flexWrap="wrap">
          {/* Text formatting */}
          <IconButton
            size="sm"
            aria-label="Bold"
            onClick={() => editor.chain().focus().toggleBold().run()}
            variant={editor.isActive('bold') ? 'solid' : 'ghost'}
            colorPalette={editor.isActive('bold') ? 'blue' : 'gray'}
          >
            <FaBold />
          </IconButton>

          <IconButton
            size="sm"
            aria-label="Italic"
            onClick={() => editor.chain().focus().toggleItalic().run()}
            variant={editor.isActive('italic') ? 'solid' : 'ghost'}
            colorPalette={editor.isActive('italic') ? 'blue' : 'gray'}
          >
            <FaItalic />
          </IconButton>

          <IconButton
            size="sm"
            aria-label="Strikethrough"
            onClick={() => editor.chain().focus().toggleStrike().run()}
            variant={editor.isActive('strike') ? 'solid' : 'ghost'}
            colorPalette={editor.isActive('strike') ? 'blue' : 'gray'}
          >
            <FaStrikethrough />
          </IconButton>

          <IconButton
            size="sm"
            aria-label="Code"
            onClick={() => editor.chain().focus().toggleCode().run()}
            variant={editor.isActive('code') ? 'solid' : 'ghost'}
            colorPalette={editor.isActive('code') ? 'blue' : 'gray'}
          >
            <FaCode />
          </IconButton>

          <Separator orientation="vertical" height="24px" />

          {/* Headings */}
          <Button
            size="sm"
            onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
            variant={editor.isActive('heading', { level: 1 }) ? 'solid' : 'ghost'}
            colorPalette={editor.isActive('heading', { level: 1 }) ? 'blue' : 'gray'}
          >
            H1
          </Button>

          <Button
            size="sm"
            onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
            variant={editor.isActive('heading', { level: 2 }) ? 'solid' : 'ghost'}
            colorPalette={editor.isActive('heading', { level: 2 }) ? 'blue' : 'gray'}
          >
            H2
          </Button>

          <Button
            size="sm"
            onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
            variant={editor.isActive('heading', { level: 3 }) ? 'solid' : 'ghost'}
            colorPalette={editor.isActive('heading', { level: 3 }) ? 'blue' : 'gray'}
          >
            H3
          </Button>

          <Separator orientation="vertical" height="24px" />

          {/* Lists */}
          <IconButton
            size="sm"
            aria-label="Bullet List"
            onClick={() => editor.chain().focus().toggleBulletList().run()}
            variant={editor.isActive('bulletList') ? 'solid' : 'ghost'}
            colorPalette={editor.isActive('bulletList') ? 'blue' : 'gray'}
          >
            <FaListUl />
          </IconButton>

          <IconButton
            size="sm"
            aria-label="Numbered List"
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
            variant={editor.isActive('orderedList') ? 'solid' : 'ghost'}
            colorPalette={editor.isActive('orderedList') ? 'blue' : 'gray'}
          >
            <FaListOl />
          </IconButton>

          <IconButton
            size="sm"
            aria-label="Blockquote"
            onClick={() => editor.chain().focus().toggleBlockquote().run()}
            variant={editor.isActive('blockquote') ? 'solid' : 'ghost'}
            colorPalette={editor.isActive('blockquote') ? 'blue' : 'gray'}
          >
            <FaQuoteLeft />
          </IconButton>

          <Separator orientation="vertical" height="24px" />

          {/* Media */}
          <IconButton
            size="sm"
            aria-label="Add Link"
            onClick={addLink}
            variant={editor.isActive('link') ? 'solid' : 'ghost'}
            colorPalette={editor.isActive('link') ? 'blue' : 'gray'}
          >
            <FaLink />
          </IconButton>

          <IconButton
            size="sm"
            aria-label="Add Image"
            onClick={addImage}
            variant="ghost"
          >
            <FaImage />
          </IconButton>

          <Separator orientation="vertical" height="24px" />

          {/* Undo/Redo */}
          <IconButton
            size="sm"
            aria-label="Undo"
            onClick={() => editor.chain().focus().undo().run()}
            disabled={!editor.can().undo()}
            variant="ghost"
          >
            <FaUndo />
          </IconButton>

          <IconButton
            size="sm"
            aria-label="Redo"
            onClick={() => editor.chain().focus().redo().run()}
            disabled={!editor.can().redo()}
            variant="ghost"
          >
            <FaRedo />
          </IconButton>
        </HStack>
      </Box>

      {/* Editor Content */}
      <Box
        padding={4}
        minHeight={minHeight}
        backgroundColor={colorMode === 'dark' ? 'gray.800' : 'white'}
        sx={{
          '& .tiptap-editor': {
            outline: 'none',
            '& p.is-editor-empty:first-of-type::before': {
              content: 'attr(data-placeholder)',
              color: colorMode === 'dark' ? 'gray.500' : 'gray.400',
              float: 'left',
              height: 0,
              pointerEvents: 'none'
            },
            '& h1': {
              fontSize: '2rem',
              fontWeight: 'bold',
              marginTop: '1rem',
              marginBottom: '0.5rem'
            },
            '& h2': {
              fontSize: '1.5rem',
              fontWeight: 'bold',
              marginTop: '0.75rem',
              marginBottom: '0.5rem'
            },
            '& h3': {
              fontSize: '1.25rem',
              fontWeight: 'bold',
              marginTop: '0.5rem',
              marginBottom: '0.5rem'
            },
            '& ul, & ol': {
              paddingLeft: '1.5rem',
              marginTop: '0.5rem',
              marginBottom: '0.5rem'
            },
            '& blockquote': {
              borderLeftWidth: '4px',
              borderLeftColor: colorMode === 'dark' ? 'gray.600' : 'gray.300',
              paddingLeft: '1rem',
              marginLeft: 0,
              fontStyle: 'italic',
              color: colorMode === 'dark' ? 'gray.400' : 'gray.600'
            },
            '& code': {
              backgroundColor: colorMode === 'dark' ? 'gray.700' : 'gray.100',
              padding: '0.125rem 0.25rem',
              borderRadius: '0.25rem',
              fontFamily: 'monospace',
              fontSize: '0.875rem'
            },
            '& pre': {
              backgroundColor: colorMode === 'dark' ? 'gray.900' : 'gray.100',
              padding: '0.75rem',
              borderRadius: '0.375rem',
              overflowX: 'auto',
              '& code': {
                backgroundColor: 'transparent',
                padding: 0
              }
            },
            '& a.tiptap-link': {
              color: 'blue.500',
              textDecoration: 'underline',
              cursor: 'pointer',
              '&:hover': {
                color: 'blue.600'
              }
            },
            '& img.tiptap-image': {
              maxWidth: '100%',
              height: 'auto',
              borderRadius: '0.375rem',
              marginTop: '0.5rem',
              marginBottom: '0.5rem'
            }
          }
        }}
      >
        <EditorContent editor={editor} />
      </Box>
    </Box>
  )
}
