// Browser half of dsh-ai-pm.
// Adds an "AI-PM" tab under Settings → Plugins: requirement board (list +
// status), create skeleton, run machine gate, and the HUMAN review form —
// the only path that may set `confirmed`. The panel talks to the host
// through /api/ai-pm; all drafting is done by the agent via ai_pm_* tools.

window.__ModuleLoader__.load({ id: 'dsh-ai-pm', factory: (require) => {
  var module = { exports: {} }; var exports = module.exports;

  const React = require('react')
  const { useState, useEffect } = React
  const h = React.createElement

  function api(method, params) {
    return fetch('/api/ai-pm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(Object.assign({ method }, params || {})),
    }).then((r) => r.json())
  }

  const CSS = `
.apm{font-size:14px;line-height:1.6;color:var(--dsw-alias-label-primary);max-width:56rem}
.apm-card{background:var(--dsw-alias-bg-layer-3);border:1px solid var(--dsw-alias-border-l2);border-radius:12px;padding:14px 16px;margin-top:10px}
.apm-title{font-size:15px;font-weight:600;margin:0 0 4px}
.apm-desc{font-size:12.5px;color:var(--dsw-alias-label-secondary);margin:0 0 10px}
.apm-req{display:flex;align-items:center;gap:8px;padding:7px 10px;border:1px solid var(--dsw-alias-border-l2);border-radius:8px;margin-top:6px;cursor:pointer}
.apm-req:hover{border-color:var(--dsw-alias-label-primary)}
.apm-req.sel{border-color:var(--dsw-static-deepseek-500);background:var(--dsw-alias-bg-layer-2)}
.apm-tag{font-size:11px;padding:1px 7px;border-radius:99px;border:1px solid var(--dsw-alias-border-l2);color:var(--dsw-alias-label-secondary)}
.apm-btn{appearance:none;background:var(--dsw-alias-label-primary);border:1px solid var(--dsw-alias-label-primary);color:var(--dsw-alias-bg-layer-3);font:inherit;font-size:13px;font-weight:600;padding:6px 16px;border-radius:8px;cursor:pointer;margin-right:8px}
.apm-btn:hover:not(:disabled){opacity:.85}
.apm-btn:disabled{opacity:.4;cursor:default}
.apm-btn.ghost{background:transparent;color:var(--dsw-alias-label-primary)}
.apm-input{background:var(--dsw-alias-bg-layer-2);border:1px solid var(--dsw-alias-border-l2);color:var(--dsw-alias-label-primary);font:inherit;font-size:13px;padding:6px 10px;border-radius:8px;margin-right:8px}
.apm-input.wide{width:100%;box-sizing:border-box;margin:0 0 8px}
.apm-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.apm-pre{font-family:ui-monospace,monospace;font-size:11.5px;color:var(--dsw-alias-label-secondary);background:var(--dsw-alias-bg-layer-2);border:1px solid var(--dsw-alias-border-l2);border-radius:8px;padding:10px;margin-top:8px;white-space:pre-wrap;word-break:break-all;max-height:420px;overflow:auto}
.apm-ok{color:var(--dsw-alias-state-success-primary);font-size:12.5px;margin-top:8px;white-space:pre-wrap}
.apm-err{color:var(--dsw-alias-label-error);font-size:12.5px;margin-top:8px;white-space:pre-wrap}
.apm-note{font-size:11.5px;color:var(--dsw-alias-label-tertiary);margin-top:8px}
`

  const WORK_ITEMS = [
    'project-background-goal',
    'user-journey-and-stories',
    'product-ux',
    'function-description',
    'prd-assembly',
  ]

  function statusSummary(s) {
    if (!s) return ''
    if (s.error) return s.error
    const act = s.active_work_item || ''
    const items = s.work_items || {}
    const states = Object.keys(items).map((k) => k + ':' + (items[k] || '∅')).join(' ')
    return states
  }

  function AiPmPanel() {
    const [list, setList] = useState(null)
    const [sel, setSel] = useState(null)
    const [newId, setNewId] = useState('')
    const [busy, setBusy] = useState(false)
    const [detail, setDetail] = useState(null)
    const [gateOut, setGateOut] = useState(null)
    const [reviewOut, setReviewOut] = useState(null)
    // review form
    const [rf, setRf] = useState({ workItem: WORK_ITEMS[0], decision: 'approve', reviewer: '', reviewerId: '', reviewerRole: 'business_owner', comments: '', reason: '' })

    const refreshList = () => {
      api('list').then((r) => {
        setList(r.ok ? r.requirements : [])
      })
    }
    useEffect(() => { refreshList() }, [])

    const loadDetail = (reqId) => {
      setSel(reqId)
      setDetail(null)
      setGateOut(null)
      setReviewOut(null)
      api('status', { reqId }).then((r) => setDetail(r))
    }

    const createReq = () => {
      const id = newId.trim()
      if (!id) return
      setBusy(true)
      api('init', { reqId: id }).then((r) => {
        setBusy(false)
        setNewId('')
        refreshList()
        setDetail(r)
      })
    }

    const runGate = () => {
      if (!sel || !rf.workItem) return
      setBusy(true)
      api('gate', { reqId: sel, workItem: rf.workItem }).then((r) => {
        setBusy(false)
        setGateOut(r)
      })
    }

    const submitReview = (decision) => {
      if (!sel) return
      if (decision === 'changes' && !rf.reason.trim()) {
        setReviewOut({ ok: false, error: 'decision=changes 时必须填写 reason（打回原因）' })
        return
      }
      setBusy(true)
      api('review', Object.assign({ reqId: sel }, rf, { decision })).then((r) => {
        setBusy(false)
        setReviewOut(r)
        loadDetail(sel)
      })
    }

    return h('div', { className: 'apm' },
      h('div', { className: 'apm-card' },
        h('h3', { className: 'apm-title' }, 'AI-PM · PRD 工作台'),
        h('p', { className: 'apm-desc' },
          '把原始需求材料转化为经人工确认、可追溯的中文 prd.md。' +
          'Agent 通过 ai_pm_* 工具起草与跑闸门；下方的「人工确认」是唯一能产生 confirmed 的路径。'
        ),
        h('div', null,
          h('input', { className: 'apm-input', placeholder: '新建需求，如 REQ-005-order-refund', value: newId, onChange: (e) => setNewId(e.target.value) }),
          h('button', { className: 'apm-btn', disabled: busy || !newId.trim(), onClick: createReq }, '创建骨架'),
        ),
        h('div', null,
          !list ? h('div', { className: 'apm-note' }, '加载中…') :
          list.length === 0 ? h('div', { className: 'apm-note' }, '还没有需求，先用上面的输入框创建。') :
          list.map((it) => h('div', {
            key: it.reqId,
            className: 'apm-req' + (sel === it.reqId ? ' sel' : ''),
            onClick: () => loadDetail(it.reqId),
          },
            h('span', { style: { fontWeight: 600 } }, it.reqId),
            h('span', { className: 'apm-tag' }, it.ok ? statusSummary(it.status) : ('ERROR: ' + (it.error || ''))),
          )),
        ),
      ),

      sel ? h('div', { className: 'apm-card' },
        h('h3', { className: 'apm-title' }, sel + ' · 状态'),
        detail && detail.ok
          ? h('div', null,
              detail.json && detail.json.active_work_item
                ? h('div', null,
                    h('span', { className: 'apm-tag' }, 'active: ' + detail.json.active_work_item),
                    h('span', { className: 'apm-tag', style: { marginLeft: 6 } }, 'next: ' + (detail.json.next_work_item || '—')),
                  )
                : null,
              h('pre', { className: 'apm-pre' }, JSON.stringify(detail.json || detail, null, 2)),
            )
          : h('div', { className: detail && !detail.ok ? 'apm-err' : 'apm-note' },
              detail ? (detail.error || detail.output || '状态加载失败') : '加载中…'),

        h('div', { className: 'apm-title', style: { marginTop: 14 } }, '机器闸门'),
        h('select', { className: 'apm-input', value: rf.workItem, onChange: (e) => setRf(Object.assign({}, rf, { workItem: e.target.value })) },
          WORK_ITEMS.map((w) => h('option', { key: w, value: w }, w))),
        h('button', { className: 'apm-btn ghost', disabled: busy, onClick: runGate }, '跑 gate（只读）'),
        gateOut ? h('pre', { className: 'apm-pre' }, gateOut.output || JSON.stringify(gateOut.json || gateOut, null, 2)) : null,

        h('div', { className: 'apm-title', style: { marginTop: 14 } }, '人工确认（唯一写 confirmed 的路径）'),
        h('div', { className: 'apm-grid' },
          h('input', { className: 'apm-input wide', placeholder: '评审人姓名', value: rf.reviewer, onChange: (e) => setRf(Object.assign({}, rf, { reviewer: e.target.value })) }),
          h('input', { className: 'apm-input wide', placeholder: '评审人 ID（须与 authorized-reviewers.json 一致）', value: rf.reviewerId, onChange: (e) => setRf(Object.assign({}, rf, { reviewerId: e.target.value })) }),
        ),
        h('input', { className: 'apm-input wide', placeholder: '角色（如 business_owner / product_owner）', value: rf.reviewerRole, onChange: (e) => setRf(Object.assign({}, rf, { reviewerRole: e.target.value })) }),
        h('input', { className: 'apm-input wide', placeholder: '意见（可选）', value: rf.comments, onChange: (e) => setRf(Object.assign({}, rf, { comments: e.target.value })) }),
        h('input', { className: 'apm-input wide', placeholder: '原因 reason（decision=changes 时必填）', value: rf.reason, onChange: (e) => setRf(Object.assign({}, rf, { reason: e.target.value })) }),
        h('button', { className: 'apm-btn', disabled: busy || !rf.reviewer || !rf.reviewerId, onClick: () => submitReview('approve') }, '✓ 通过 approve'),
        h('button', { className: 'apm-btn ghost', disabled: busy || !rf.reviewer || !rf.reviewerId, onClick: () => submitReview('changes') }, '↩ 打回 changes'),
        reviewOut ? h('div', { className: reviewOut.ok ? 'apm-ok' : 'apm-err' },
          (reviewOut.output || reviewOut.error || JSON.stringify(reviewOut))) : null,
        h('div', { className: 'apm-note' },
          '确认前请先在 00-input/authorized-reviewers.json 登记评审人；机器检查只能产出 ready_for_human_review。'),
      ) : null,
    )
  }

  const inject = ['slots']

  function apply(ctx) {
    const slots = ctx.get('slots')
    if (slots === undefined) return
    ctx.effect(() => {
      const id = 'dsh-ai-pm-style'
      if (!document.getElementById(id)) {
        const s = document.createElement('style')
        s.id = id
        s.textContent = CSS
        document.head.appendChild(s)
      }
      return () => { const el = document.getElementById(id); if (el) el.remove() }
    }, 'ai-pm-style')
    slots.inject('settings.plugins.tab', () => slots.register(
      { name: 'settings.plugins.tab', id: 'ai-pm', order: 2, label: () => 'AI-PM' },
      AiPmPanel,
    ))
  }

  module.exports = { inject, apply }
  return module.exports;
} })
