"use client"

import React, { useEffect } from 'react'
import { useEditor, EditorContent, type Editor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Placeholder from '@tiptap/extension-placeholder'
import { Extension } from '@tiptap/core'
import { Plugin, PluginKey } from '@tiptap/pm/state'
// Prefer tiptap's pm view wrapper if available; fallback to prosemirror-view
import { Decoration, DecorationSet } from 'prosemirror-view'
import { Bold, Italic, Type, List, Link2 } from 'lucide-react'
import { Node } from '@tiptap/pm/model'

type FailedProp = { sentence: string; reason: string }

type Props = {
  value: string
  onChange: (html: string) => void
  failedPropositions?: FailedProp[]
  onEditorReady?: (editor: Editor | null) => void
}

// Helper to escape regex chars
function escapeForRegex(s: string) {
  return s.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&')
}

const failedPluginKey = new PluginKey('failedProps')

// Local Tiptap Extension that manages failed proposition decorations safely
const FailedPropositionsExtension = Extension.create<{
  failed: FailedProp[]
}>({
  name: 'failedPropositionsExtension',

  addOptions() {
    return {
      failed: [] as FailedProp[]
    }
  },

  // expose a runtime command to update failed propositions; use `any` typing to satisfy TS
  addCommands(): any {
    return {
      // Command to update failed propositions at runtime without changing plugins
      setFailedPropositions:
        (failed: FailedProp[]) => ({ tr, dispatch }: { tr: any; dispatch: any }) => {
          if (dispatch) {
            tr.setMeta(failedPluginKey, failed)
            dispatch(tr)
          }
          return true
        }
    } as any
  },

  addProseMirrorPlugins() {
    const initialFailed = this.options.failed || []

    function computeDecorations(doc: any, failedList: FailedProp[]) {
      const decs: Decoration[] = []
      const fullText = doc.textBetween(0, doc.content.size, '\n', '\n')

      for (const f of failedList) {
        try {
          const re = new RegExp(escapeForRegex(f.sentence), 'g')
          let m: RegExpExecArray | null
          while ((m = re.exec(fullText)) !== null) {
            const start = m.index
            const end = start + m[0].length

            // Walk text nodes and map plain-text offsets to document positions
            let cumulative = 0
            doc.descendants((node: Node, posFrom: number) => {
              if (node.isText) {
                const nodeText = node.text || ''
                const nodeStart = cumulative
                const nodeEnd = cumulative + nodeText.length
                if (nodeEnd > start && nodeStart < end) {
                  const from = posFrom + Math.max(0, start - nodeStart)
                  const to = posFrom + Math.min(nodeText.length, end - nodeStart)
                  // validate range
                  const docSize = doc.content.size
                  if (from < to && from >= 0 && to <= docSize) {
                    decs.push(Decoration.inline(from, to, { class: 'bg-amber-100 text-amber-900 px-1 rounded' }))
                  }
                }
                cumulative += nodeText.length
              }
            })
          }
        } catch (e) {
          // ignore invalid regex
        }
      }

      if (!decs || decs.length === 0) return DecorationSet.empty
      return DecorationSet.create(doc, decs)
    }

    return [
      new Plugin({
        key: failedPluginKey,
        state: {
          init(_, state) {
            return computeDecorations(state.doc, initialFailed)
          },
          apply(tr, old, oldState, newState) {
            const meta = tr.getMeta(failedPluginKey)
            if (meta) {
              return computeDecorations(newState.doc, meta)
            }

            if (tr.docChanged) {
              return old.map(tr.mapping, tr.doc)
            }

            return old
          }
        },
        props: {
          decorations(state) {
            // @ts-ignore
            return failedPluginKey.getState(state)
          }
        }
      })
    ]
  }
})

export default function RichEditorTiptap({ value, onChange, failedPropositions = [], onEditorReady }: Props) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Link.configure({ openOnClick: false }),
      Placeholder.configure({ placeholder: 'Start editing the caption...' }),
      // register the custom extension here with initial data
      FailedPropositionsExtension.configure({ failed: failedPropositions })
    ],
    content: value || '',
    onUpdate({ editor }) {
      onChange(editor.getHTML())
    },
    editorProps: {
      attributes: { class: 'prose max-w-full' }
    }
  })

  // When failedPropositions changes, update plugin state via command (no view.setProps)
  useEffect(() => {
    if (!editor) return
    const cmds: any = editor.commands
    if (typeof cmds.setFailedPropositions === 'function') {
      cmds.setFailedPropositions(failedPropositions)
    } else {
      const view = editor.view
      if (view) view.dispatch(view.state.tr.setMeta(failedPluginKey, failedPropositions))
    }
  }, [editor, failedPropositions])

  useEffect(() => {
    if (!editor) return
    // Update content when value changes externally
    const html = value || ''
    if (editor.getHTML() !== html) {
      editor.commands.setContent(html, false)
    }
  }, [value, editor])

  useEffect(() => { onEditorReady?.(editor) }, [editor, onEditorReady])

  return (
    <div className="relative">
      <div className="absolute -top-10 left-0 right-0 flex justify-start gap-2">
        <div className="inline-flex items-center gap-2 bg-white/60 backdrop-blur rounded-full px-2 py-1 border border-slate-100 shadow-sm">
          <button onClick={() => editor?.chain().focus().toggleHeading({ level: 1 }).run()} className={`p-2 rounded hover:bg-slate-50 ${editor?.isActive('heading', { level: 1 }) ? 'bg-slate-100' : ''}`} aria-label="Heading 1"><Type size={16} /></button>
          <button onClick={() => editor?.chain().focus().toggleHeading({ level: 2 }).run()} className={`p-2 rounded hover:bg-slate-50 ${editor?.isActive('heading', { level: 2 }) ? 'bg-slate-100' : ''}`} aria-label="Heading 2">H2</button>
          <button onClick={() => editor?.chain().focus().toggleBold().run()} className={`p-2 rounded hover:bg-slate-50 ${editor?.isActive('bold') ? 'bg-slate-100' : ''}`} aria-label="Bold"><Bold size={16} /></button>
          <button onClick={() => editor?.chain().focus().toggleItalic().run()} className={`p-2 rounded hover:bg-slate-50 ${editor?.isActive('italic') ? 'bg-slate-100' : ''}`} aria-label="Italic"><Italic size={16} /></button>
          <button onClick={() => editor?.chain().focus().toggleBulletList().run()} className={`p-2 rounded hover:bg-slate-50 ${editor?.isActive('bulletList') ? 'bg-slate-100' : ''}`} aria-label="List"><List size={16} /></button>
          <button onClick={() => editor?.chain().focus().toggleBlockquote().run()} className={`p-2 rounded hover:bg-slate-50 ${editor?.isActive('blockquote') ? 'bg-slate-100' : ''}`} aria-label="Quote">“</button>
          <button onClick={() => {
            const url = window.prompt('Enter URL')
            if (url) editor?.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
          }} className={`p-2 rounded hover:bg-slate-50 ${editor?.isActive('link') ? 'bg-slate-100' : ''}`} aria-label="Link"><Link2 size={16} /></button>
        </div>
      </div>

      <div className="pt-6">
        <div className="min-h-[220px] prose p-6 rounded-lg border border-slate-100 bg-white">
          <EditorContent editor={editor} />
        </div>
      </div>
    </div>
  )
}
