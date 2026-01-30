import { useEffect, useState } from "react";
import { api } from "../api";
import toast from "react-hot-toast";
type Ref = any;

export default function Dashboard() {
  const [refs, setRefs] = useState<Ref[]>([]);
  const [title, setTitle] = useState("");
  const [authors, setAuthors] = useState("");
  const [year, setYear] = useState<number | undefined>(undefined);
  const [doi, setDoi] = useState("");
  const [doiLoading, setDoiLoading] = useState(false);
  function normalizeDoi(input: string) {
    return input
      .trim()
      .replace(/^https?:\/\/doi\.org\//i, "")
      .replace(/^doi:\s*/i, "")
      .trim();
  }
  async function handleDoiFill() {
    const d = normalizeDoi(doi);
    if (!d) {
      toast.error("请先输入 DOI");
      return;
    }

    setDoiLoading(true);
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/doi/resolve?doi=${encodeURIComponent(d)}`,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
            // 如果后端需要 token 再打开：
            // Authorization: `Bearer ${localStorage.getItem("token") ?? ""}`,
          },
        }
      );

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        const msg = data?.detail || data?.message || `请求失败（${res.status}）`;
        toast.error(msg);
        return;
      }

      if (data?.ok) {
        if (typeof data.title === "string" && data.title.trim()) setTitle(data.title);
        if (typeof data.authors === "string" && data.authors.trim()) setAuthors(data.authors);

        // ✅ year: 保持 number | undefined
        if (data.year !== undefined && data.year !== null) {
          const y = typeof data.year === "number" ? data.year : Number(data.year);
          setYear(Number.isFinite(y) ? y : undefined);
        }

        if (typeof data.doi === "string" && data.doi.trim()) setDoi(data.doi);

        toast.success(`补全成功（来源：${data.source ?? "unknown"}）`);
      }
      else {
        toast(
          data?.detail ??
            "开放数据库未收录（Crossref/OpenAlex/S2/doi.org 均无元数据）。可导出 RIS/BibTeX 导入。",
          { icon: "ℹ️" }
        );
      }
    } catch (e: any) {
      toast.error(`网络错误：${e?.message ?? e}`);
    } finally {
      setDoiLoading(false);
    }
  }



  async function reload() {
    const r = await api("/references");
    setRefs(r);
  }

  useEffect(() => {
    reload();
  }, []);

  return (
    <div style={{ padding: 24 }}>
      <h2>CiteCheck</h2>

      <div style={{ border: "1px solid #ddd", padding: 12, marginBottom: 16 }}>
        <h3>新建文献（MVP）</h3>
        <input placeholder="title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <br />
        <input placeholder="authors: 张三;李四" value={authors} onChange={(e) => setAuthors(e.target.value)} />
        <br />
        <input
          type="number"
          placeholder="year"
          value={year ?? ""}
          onChange={(e) => setYear(e.target.value ? Number(e.target.value) : undefined)}
        />

        <br />
        <input placeholder="doi（可选）" value={doi} onChange={(e) => setDoi(e.target.value)} />
        <br />
        <button
          onClick={async () => {
            await api("/references", {
              method: "POST",
              body: JSON.stringify({ ref_type: "journal", title, authors, year, doi }),
            });
            setTitle(""); setAuthors(""); setYear(undefined); setDoi("");
            reload();
          }}
        >
          保存
        </button>

        <button
          type="button"
          onClick={handleDoiFill}
          disabled={doiLoading}
          style={{
            opacity: doiLoading ? 0.7 : 1,
            cursor: doiLoading ? "not-allowed" : "pointer",
          }}
        >
          {doiLoading ? "补全中..." : "DOI 一键补全"}
        </button>

      </div>

      <h3>我的文献</h3>
      {refs.map((r) => (
        <div key={r.id} style={{ border: "1px solid #ddd", padding: 12, marginBottom: 12 }}>
          <div><b>{r.title}</b></div>
          <div>authors: {r.authors}</div>
          <div>missing: <span style={{ color: r.missing?.length ? "red" : "green" }}>{(r.missing || []).join(", ") || "none"}</span></div>
          <div style={{ marginTop: 8 }}><code>{r.gbt7714}</code></div>
          <button
            style={{ marginTop: 8 }}
            onClick={async () => {
              await api(`/references/${r.id}`, { method: "DELETE" });
              reload();
            }}
          >
            删除
          </button>
        </div>
      ))}
    </div>
  );
}
