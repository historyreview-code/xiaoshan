#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《崤山》长篇卷目 HTML 生成器：读取分卷 md，生成章节体 HTML 页面。"""
import html
import re

VOLUMES = [
    ("卷一", "质子之妻", "崤山_长篇_卷一.md", "volume1.html"),
    ("卷二", "流亡之君", "崤山_长篇_卷二.md", "volume2.html"),
    ("卷三", "裂痕", "崤山_长篇_卷三.md", "volume3.html"),
]
NEXT = {"volume1.html": "volume2.html", "volume2.html": "volume3.html"}
PREV = {"volume2.html": "volume1.html", "volume3.html": "volume2.html"}


def esc(s):
    return html.escape(s, quote=False)


def parse_md(path):
    """解析分卷 md：标题、体例说明（引用块）、章节。"""
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    title = ""
    note = ""
    chapters = []  # (heading, [paragraphs])
    cur_head = None
    cur_paras = []
    buf = []

    def flush_para():
        nonlocal buf
        if buf:
            cur_paras.append("\n".join(buf).strip())
            buf = []

    def flush_chapter():
        nonlocal cur_head, cur_paras
        flush_para()
        if cur_head is not None:
            chapters.append((cur_head, cur_paras))
        cur_head = None
        cur_paras = []

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            flush_para()
            continue
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue
        if line.startswith("> "):
            note += (note and "\n" or "") + line[2:].strip()
            continue
        m = re.match(r"^##\s+(.+)$", line)
        if m:
            flush_chapter()
            cur_head = m.group(1).strip()
            continue
        buf.append(line)
    flush_chapter()
    return title, note, chapters


STYLE = """
  :root{--paper:#f5f0e4;--paper2:#efe8d8;--ink:#2a2418;--ink2:#5c5340;--accent:#9c3b2a;--accent2:#7a5c3a;--line:#d8cdb4;}
  *{margin:0;padding:0;box-sizing:border-box;}
  html{scroll-behavior:smooth;}
  body{background:var(--paper);color:var(--ink);font-family:"Songti SC","Noto Serif SC","STSong","SimSun",serif;line-height:2.0;letter-spacing:.02em;}
  ::selection{background:rgba(156,59,42,.18);}
  header{background:var(--ink);color:var(--paper);padding:2rem 1.2rem;text-align:center;border-bottom:4px solid var(--accent);}
  header h1{font-size:2.2rem;letter-spacing:.3em;text-indent:.3em;margin-bottom:.4rem;}
  header p{color:#cfc6ae;font-size:.95rem;letter-spacing:.15em;}
  .wrap{display:flex;max-width:1200px;margin:0 auto;min-height:80vh;}
  nav#toc{width:250px;flex:0 0 250px;background:var(--paper2);border-right:1px solid var(--line);padding:1.6rem 1rem 2rem;position:sticky;top:0;align-self:flex-start;height:100vh;overflow-y:auto;}
  nav#toc .toc-title{font-size:.95rem;letter-spacing:.3em;color:var(--accent);border-bottom:1px solid var(--line);padding-bottom:.6rem;margin-bottom:.8rem;text-align:center;}
  nav#toc a{display:block;color:var(--ink2);text-decoration:none;padding:.45rem .6rem;font-size:.92rem;border-radius:4px;border-left:2px solid transparent;}
  nav#toc a:hover{color:var(--accent);background:rgba(156,59,42,.06);border-left-color:var(--accent);}
  nav#toc a.active{color:var(--accent);border-left-color:var(--accent);background:rgba(156,59,42,.08);}
  nav#toc .toc-sub{font-size:.8rem;color:#8a8169;padding:.2rem .6rem;letter-spacing:.1em;}
  main{flex:1;min-width:0;padding:2.5rem 2.8rem 4rem;max-width:820px;}
  section.chapter{padding-top:1rem;border-top:1px solid var(--line);margin-top:2.5rem;}
  section.chapter:first-of-type{border-top:none;margin-top:0;padding-top:.5rem;}
  .ch-head{text-align:center;margin:0 0 2rem;}
  .ch-no{font-size:.85rem;letter-spacing:.4em;color:var(--accent2);margin-bottom:.4rem;}
  .ch-head h2{font-size:1.9rem;letter-spacing:.25em;text-indent:.25em;}
  .ch-deco{width:56px;height:2px;background:var(--accent);margin:.9rem auto 0;}
  section.chapter p{text-indent:2em;margin-bottom:.9rem;}
  .note{border-left:3px solid var(--accent2);background:rgba(122,92,58,.05);color:var(--ink2);padding:.6rem 1.2rem;margin:1.2rem 2rem;font-size:.92rem;}
  .pager{display:flex;justify-content:space-between;gap:1rem;margin-top:3rem;padding-top:1.4rem;border-top:1px dashed var(--line);font-size:.95rem;}
  .pager a{color:var(--accent);text-decoration:none;letter-spacing:.08em;}
  .pager a:hover{text-decoration:underline;}
  .pager .next{margin-left:auto;text-align:right;}
  footer{background:var(--ink);color:#9d937c;text-align:center;padding:1.6rem 1rem;font-size:.85rem;letter-spacing:.15em;}
  footer a{color:#cfc6ae;}
  #menuBtn{display:none;}
  @media (max-width:860px){
    header h1{font-size:1.6rem;}
    .wrap{flex-direction:column;}
    nav#toc{width:100%;flex:none;height:auto;position:static;border-right:none;border-bottom:1px solid var(--line);padding:0;}
    #menuBtn{display:block;width:100%;background:var(--paper2);border:none;padding:.8rem;font-size:.9rem;letter-spacing:.3em;color:var(--accent);font-family:inherit;cursor:pointer;}
    #tocList{display:none;}
    nav#toc.open #tocList{display:block;padding:0 1rem 1rem;}
    main{padding:1.6rem 1.2rem 3rem;}
    .ch-head h2{font-size:1.5rem;}
    .note{margin:1.2rem .6rem;}
  }
"""


def build_page(vol, name, path, out):
    title, note, chapters = parse_md(path)
    toc_links = []
    sections = []
    for head, paras in chapters:
        anchor = "ch%d" % len(toc_links)
        toc_links.append('<a href="#%s">%s</a>' % (anchor, esc(head)))
        parts = ['<section class="chapter" id="%s">' % anchor,
                 '<div class="ch-head"><div class="ch-no">%s</div><h2>%s</h2><div class="ch-deco"></div></div>' % (esc(vol), esc(head))]
        for p in paras:
            if p:
                parts.append("<p>%s</p>" % esc(p))
        parts.append("</section>")
        sections.append("\n".join(parts))
    prev_html = '<a href="%s">← %s</a>' % (PREV[out], "上一卷") if out in PREV else "<span></span>"
    next_html = '<a class="next" href="%s">下一卷 →</a>' % NEXT[out] if out in NEXT else '<a class="next" href="index.html">返回首页 →</a>'
    note_html = ('<div class="note">%s</div>' % esc(note).replace("\n", "<br>")) if note else ""
    page = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · {name} · 崤山</title>
<meta name="description" content="历史小说《崤山》长篇 {vol}《{name}》">
<style>{style}</style>
</head>
<body>
<header><h1>{vol} · {name}</h1><p>《崤山》长篇 · 据《左传》《史记》创作</p></header>
<div class="wrap">
<nav id="toc"><div class="toc-title">目 录</div>
<button id="menuBtn" aria-expanded="false">章 节 目 录</button>
<div id="tocList">
<a href="index.html">← 首页</a>
{toc}
</div></nav>
<main>
{note}
{sections}
<div class="pager">{prev}{next}</div>
</main>
</div>
<footer>《崤山》长篇 · {vol} · <a href="index.html">返回首页</a></footer>
<script>
var btn=document.getElementById('menuBtn');
btn.addEventListener('click',function(){{document.getElementById('toc').classList.toggle('open');btn.setAttribute('aria-expanded',document.getElementById('toc').classList.contains('open'));}});
var links=document.querySelectorAll('nav#toc a[href^="#"]');
var sections=[].map.call(links,function(a){{return document.getElementById(a.getAttribute('href').slice(1));}});
window.addEventListener('scroll',function(){{var pos=window.scrollY+120,cur=0;sections.forEach(function(s,i){{if(s&&s.offsetTop<=pos)cur=i;}});links.forEach(function(a,i){{a.classList.toggle('active',i===cur);}});}},{{passive:true}});
</script>
</body>
</html>""".format(
        title=esc(title), name=esc(name), vol=esc(vol), style=STYLE,
        toc="\n".join(toc_links), sections="\n".join(sections),
        note=note_html, prev=prev_html, next=next_html,
    )
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print("生成 %s（%d 章）" % (out, len(chapters)))


if __name__ == "__main__":
    for vol, name, path, out in VOLUMES:
        build_page(vol, name, path, out)
    print("完成")
